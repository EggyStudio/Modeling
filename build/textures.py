#!/usr/bin/env python3
"""Builds the module's texture collection in Modeling/Textures from the sources the manifest beside
it, textures.json, names, by the recipe it gives each entry.

    build/textures.py                        # build every entry whose source is here
    build/textures.py NAME ...               # build the entries named
    build/textures.py --out DIR NAME ...     # write the entries under DIR, the collection left as it is
    build/textures.py --repeat FILE DX DY    # the shift near DX, DY at which a scan best matches itself

An entry is three KTX2 files with their mipmaps, in the formats of BevyCSharp's vegetation
collection, whose build/textures.py this one is carried from until the Tools module holds it:

    albedo.ktx2   BC7, sRGB     the color in RGB and the opacity in A
    normal.ktx2   BC5           the tangent-space normal's X and Y, its Z what makes a unit length
    surface.ktx2  BC7, linear   occlusion in R, roughness in G, metallic in B and translucency in A,
                                as glTF's occlusion and metallic-roughness textures place the first three

The albedo is the size the recipe gives, at most 1024 square, and the normal and the surface half of
it, as in the vegetation's collection. Each level's blocks are kept as they are, where BevyCSharp's
compresses them with zstd, since .NET's library holds no zstd, so the module's tests and a reader
without it take the files as written. Git compresses them in the repository all the same.

Every entry tiles. A map is resized with its opposite edges wrapped round, so it tiles at its new
size as it did at its old. A scan whose edges do not meet is made into a tile from its repeat, the
two shifts at which the pattern matches itself, which --repeat finds from a guess read off the
picture, and a third, half their sum, where the pattern is a half-drop. The tile is the
parallelogram the two shifts span, drawn straight, and each texel is the mean of every copy of its
place the scan holds, weighted down toward the scan's edges, so a texel on one edge of the tile and
its neighbor across the opposite edge are the same place, and a stain or a shade one copy carries is
diluted by the others. The repeat's size in meters is written into the manifest from the dots an
inch the scan's file records.

The encoders are BevyCSharp's, BC7's mode 6 with each block's endpoints along its principal axis and
fitted again by least squares, and BC4 twice for BC5, so the build needs Python 3 and Pillow and
nothing else. Each level is made from the one above by a box filter. Each build writes the files'
sizes, the encoders' error, the mean color and the mean surface back into the manifest, which the
tests read the decoded files against. The same sources and recipe make the same bytes.

A source is a folder under .ref/, which the repository leaves out, the one the manifest names.
"""

import argparse
import json
import math
import os
import struct
import sys

from PIL import Image, ImageChops, ImageMath, ImageStat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLLECTION = os.path.join(ROOT, "Modeling", "Textures")
MANIFEST = os.path.join(COLLECTION, "textures.json")

# Vulkan's numbers for the formats, which a KTX2 file names its texels by.
BC5_UNORM = 141
BC7_UNORM = 145
BC7_SRGB = 146

# The Khronos data format descriptor's color models and transfer functions for them.
MODEL_BC5 = 132
MODEL_BC7 = 134
TRANSFER_LINEAR = 1
TRANSFER_SRGB = 2

# BC7's interpolation weights for four-bit indices, in sixty-fourths, and the nearest index for each
# sixty-fourth, so a texel's place between the endpoints is turned into its index by a lookup.
WEIGHTS = (0, 4, 9, 13, 17, 21, 26, 30, 34, 38, 43, 47, 51, 55, 60, 64)
NEAREST = [min(range(16), key=lambda i: abs(WEIGHTS[i] - t)) for t in range(65)]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("names", nargs="*", help="the entries to build, every one whose source is here where none is named")
    parser.add_argument("--out", help="write the entries under this folder, the collection and its manifest left as they are")
    parser.add_argument("--repeat", nargs=3, metavar=("FILE", "DX", "DY"), help="print the shift near DX, DY at which the scan in FILE best matches itself")
    arguments = parser.parse_args()

    if arguments.repeat:
        path, dx, dy = arguments.repeat
        (x, y), difference = repeat_near(path, (int(dx), int(dy)))
        print(f"{x} {y}, a mean difference of {difference:.2f} of 255")
        return 0

    with open(MANIFEST, encoding="utf-8") as file:
        manifest = json.load(file)

    named = set(arguments.names)
    unknown = named - {entry["name"] for entry in manifest["entries"]}
    if unknown:
        print(f"textures.py: the manifest has no entry {', '.join(sorted(unknown))}", file=sys.stderr)
        return 2

    failed = False
    for entry in manifest["entries"]:
        if named and entry["name"] not in named:
            continue
        source = os.path.join(ROOT, entry["source"])
        if not os.path.isdir(source):
            if named:
                print(f"textures.py: {entry['name']}'s source {entry['source']} is not here", file=sys.stderr)
                failed = True
            continue

        maps = read_entry(entry, source)
        report = write_entry(maps, os.path.join(arguments.out or COLLECTION, entry["name"]))
        print(f"{entry['name']}: {', '.join(f'{file} {size // 1024} KB, {error:.1f} dB' for file, (size, error) in report.items())}")
        if not arguments.out:
            entry["files"] = {file: size for file, (size, _) in report.items()}
            entry["error"] = {file: round(error, 1) for file, (_, error) in report.items()}
            entry["color"] = mean_of(maps["albedo"].convert("RGB"))
            entry["surface"] = mean_of(maps["surface"])
            if "repeat" in entry:
                entry["meters"] = repeat_meters(entry, source)

    if not arguments.out:
        with open(MANIFEST, "w", encoding="utf-8", newline="\n") as file:
            json.dump(manifest, file, indent=2, ensure_ascii=False)
            file.write("\n")
    return 1 if failed else 0


# The recipe.

def read_entry(entry, source):
    """The entry's albedo, normal and surface at their sizes, each a tile."""
    width, height = entry["size"]
    small = (max(width // 2, 4), max(height // 2, 4))
    repeat = entry.get("repeat")

    def tile(image, size):
        return repeated(image, repeat, size) if repeat else wrapped(image, size)

    color = read_map(source, entry["albedo"])
    albedo = tile(color, (width, height))
    albedo.putalpha(255)

    if "normal" in entry:
        bumps = read_map(source, entry["normal"])
        if entry["normal"].get("flip_green"):
            r, g, b = bumps.split()
            bumps = Image.merge("RGB", (r, ImageChops.invert(g), b))
        normal = tile(bumps, small)
    else:
        normal = Image.new("RGB", small, (128, 128, 255))

    # Occlusion, roughness, metallic and translucency, a number over the whole tile or a channel of a
    # file the recipe names, which is tiled as the color is.
    layers = []
    for name, default in (("occlusion", 1.0), ("roughness", 0.8), ("metallic", 0.0), ("translucency", 0.0)):
        spec = entry.get(name, default)
        if isinstance(spec, (int, float)):
            layers.append(Image.new("L", small, round(255 * spec)))
        else:
            layers.append(tile(read_channel(source, spec), small))
    return {"albedo": albedo, "normal": normal, "surface": Image.merge("RGBA", layers)}


def read_map(source, spec):
    """A map of a recipe, its file read as RGB."""
    image = Image.open(os.path.join(source, spec["file"]))
    image.load()
    return image.convert("RGB")


def read_channel(source, spec):
    """One channel of a file a recipe names, its gray or one of its channels, turned over where it says."""
    image = Image.open(os.path.join(source, spec["file"]))
    image.load()
    channel = spec.get("channel", "l")
    image = image.convert("L") if channel == "l" else image.convert("RGBA").getchannel(channel.upper())
    return ImageChops.invert(image) if spec.get("invert") else image


def wrapped(image, size):
    """
    A tile resized with its opposite edges wrapped round, so the filter reads across an edge what lies
    across it when the tile repeats, and the tile meets itself at its new size.
    """
    if image.size == size:
        return image
    width, height = image.size
    margin = 4 * math.ceil(max(width / size[0], height / size[1])) + 2
    padded = Image.new(image.mode, (width + 2 * margin, height + 2 * margin))
    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            padded.paste(image, (margin + x * width, margin + y * height))
    return padded.resize(size, Image.Resampling.LANCZOS, box=(margin, margin, margin + width, margin + height))


def repeated(image, repeat, size):
    """
    The tile of a scan's repeat at a size, each texel the mean of every copy of its place in the scan,
    weighted by how far each lies from the scan's edges.
    """
    across, down = repeat["across"], repeat["down"]
    shifts = [(1, 0, 0), (0, 1, 0)]
    if repeat.get("half_drop"):
        shifts.append((0, 0, 1))
    half = ((across[0] + down[0]) / 2, (across[1] + down[1]) / 2)
    width, height = image.size

    # The scan reduced by a box so a texel of the tile is about a texel of it, then drawn straight.
    reduced = (max(1, round(width * size[0] / math.hypot(*across))), max(1, round(height * size[1] / math.hypot(*down))))
    scale_x, scale_y = reduced[0] / width, reduced[1] / height
    bands = [band.resize(reduced, Image.Resampling.BOX) for band in image.split()]
    weight = edge_weight(reduced, max(4, min(reduced) // 16))

    total = Image.new("F", size, 0.0)
    sums = [Image.new("F", size, 0.0) for _ in bands]
    reach = range(-2, 3)
    for i in reach:
        for j in reach:
            for k in ((0, 1) if repeat.get("half_drop") else (0,)):
                x = i * across[0] + j * down[0] + k * half[0]
                y = i * across[1] + j * down[1] + k * half[1]
                data = (across[0] / size[0] * scale_x, down[0] / size[1] * scale_x, x * scale_x,
                        across[1] / size[0] * scale_y, down[1] / size[1] * scale_y, y * scale_y)
                weights = weight.transform(size, Image.Transform.AFFINE, data, Image.Resampling.BILINEAR, fillcolor=0)
                if weights.getextrema()[1] == 0:
                    continue
                weights = weights.convert("F")
                total = ImageMath.lambda_eval(lambda a: a["t"] + a["w"], t=total, w=weights)
                for at, band in enumerate(bands):
                    copy = band.transform(size, Image.Transform.AFFINE, data, Image.Resampling.BICUBIC).convert("F")
                    sums[at] = ImageMath.lambda_eval(lambda a: a["s"] + a["c"] * a["w"], s=sums[at], c=copy, w=weights)

    # A place whose copies all lie at the scan's edges is weighted little but still its copies' mean,
    # as the wallpaper's repeat is 21 pixels taller than its scan and a strip of it lies so.
    if total.getextrema()[0] <= 0:
        raise ValueError("the scan holds no copy of some place of its repeat")
    out = [ImageMath.lambda_eval(lambda a: a["s"] / a["t"] + 0.5, s=s, t=total).convert("L") for s in sums]
    return Image.merge(image.mode, out)


def edge_weight(size, ramp):
    """A weight of 255 over a picture but a band along its edges, where it falls to nothing at the edge."""
    width, height = size
    across = Image.new("L", (width, 1))
    across.putdata([min(255, round(255 * min(x + 0.5, width - x - 0.5) / ramp)) for x in range(width)])
    down = Image.new("L", (1, height))
    down.putdata([min(255, round(255 * min(y + 0.5, height - y - 0.5) / ramp)) for y in range(height)])
    return ImageChops.multiply(across.resize(size, Image.Resampling.NEAREST), down.resize(size, Image.Resampling.NEAREST))


def repeat_near(path, guess):
    """
    The shift near a guess at which a scan differs least from itself, by the mean difference over
    where the two overlap, searched at a quarter of its size, then a half, then the whole.
    """
    image = Image.open(path).convert("L")
    width, height = image.size
    shift, difference = guess, 0.0
    for scale, reach in ((4, 24), (2, 3), (1, 3)):
        small = image.resize((width // scale, height // scale), Image.Resampling.BOX) if scale > 1 else image
        x, y = round(shift[0] / scale), round(shift[1] / scale)
        difference, x, y = min((differs(small, dx, dy), dx, dy) for dx in range(x - reach, x + reach + 1) for dy in range(y - reach, y + reach + 1))
        shift = (x * scale, y * scale)
    return shift, difference


def differs(image, dx, dy):
    width, height = image.size
    left, top = max(0, -dx), max(0, -dy)
    right, bottom = min(width, width - dx), min(height, height - dy)
    one = image.crop((left, top, right, bottom))
    other = image.crop((left + dx, top + dy, right + dx, bottom + dy))
    return ImageStat.Stat(ImageChops.difference(one, other)).mean[0]


def repeat_meters(entry, source):
    """The repeat's width and height in meters, from the dots an inch the scan's file records."""
    with Image.open(os.path.join(source, entry["albedo"]["file"])) as image:
        dots = image.info.get("dpi", (0, 0))
    if not dots[0] or not dots[1]:
        return None
    across, down = entry["repeat"]["across"], entry["repeat"]["down"]
    return [round(math.hypot(*across) / dots[0] * 0.0254, 4), round(math.hypot(*down) / dots[1] * 0.0254, 4)]


def mean_of(image):
    """The mean of each channel from zero to one."""
    return [round(value / 255, 4) for value in ImageStat.Stat(image).mean]


def resized(image, size, method):
    """
    An image resized a channel at a time, since Pillow resizes RGBA through premultiplied alpha,
    which turns the surface's channels to nothing where its translucency, in alpha, is nothing.
    """
    return Image.merge(image.mode, [band.resize(size, method) for band in image.split()])


# The levels.

def write_entry(maps, folder):
    """Writes an entry's files into a folder, and says each one's size and its encoding's error."""
    os.makedirs(folder, exist_ok=True)
    report = {}
    for name, image in maps.items():
        levels = mip_chain(image)
        format, blocks, error = encode(name, levels)
        data = ktx2(format, levels, blocks)
        path = os.path.join(folder, f"{name}.ktx2")
        with open(path + ".part", "wb") as file:
            file.write(data)
        os.replace(path + ".part", path)
        report[f"{name}.ktx2"] = (len(data), error)
    return report


def mip_chain(image):
    """The image and each level under it, half the size of the one above, down to a texel."""
    levels = [image]
    while levels[-1].size != (1, 1):
        above = levels[-1]
        levels.append(resized(above, (max(above.width // 2, 1), max(above.height // 2, 1)), Image.Resampling.BOX))
    return levels


# The encoding.

def encode(name, levels):
    """
    The format of a map and its levels' blocks, with the encoding's error in decibels at the top
    level. The one place a map's format is chosen, so another is a branch here.
    """
    if name == "normal":
        blocks = [bc5(level) for level in levels]
        return BC5_UNORM, blocks, psnr_bc5(levels[0], blocks[0])
    blocks = [bc7(level) for level in levels]
    return BC7_SRGB if name == "albedo" else BC7_UNORM, blocks, psnr_bc7(levels[0], blocks[0])


def texel_blocks(image, channels):
    """The image's 4 by 4 blocks, each its sixteen texels of the channels, a level smaller than a block repeating its edge."""
    width, height = image.size
    data = image.tobytes()
    stride = len(image.getbands())
    for by in range(0, max(height, 4), 4):
        for bx in range(0, max(width, 4), 4):
            block = []
            for y in range(by, by + 4):
                row = min(y, height - 1) * width
                for x in range(bx, bx + 4):
                    at = (row + min(x, width - 1)) * stride
                    block.append(tuple(data[at:at + channels]))
            yield block


def bc7(image):
    """The image in BC7, every block in mode 6, its RGBA endpoints with a bit each shared by their channels."""
    out = bytearray()
    for block in texel_blocks(image.convert("RGBA"), 4):
        out += bc7_block(block)
    return bytes(out)


def bc7_block(texels):
    # The endpoints along the principal axis of the block's colors, by a few rounds of the power
    # method on their covariance.
    count = 16.0
    mean = [sum(texel[c] for texel in texels) / count for c in range(4)]
    covariance = [[0.0] * 4 for _ in range(4)]
    for texel in texels:
        d = [texel[c] - mean[c] for c in range(4)]
        for i in range(4):
            for j in range(i, 4):
                covariance[i][j] += d[i] * d[j]
    for i in range(4):
        for j in range(i):
            covariance[i][j] = covariance[j][i]
    axis = [1.0, 1.0, 1.0, 1.0]
    for _ in range(6):
        axis = [sum(covariance[i][j] * axis[j] for j in range(4)) for i in range(4)]
        largest = max(abs(value) for value in axis)
        if largest == 0.0:
            break
        axis = [value / largest for value in axis]
    length = sum(value * value for value in axis)
    if length == 0.0:
        low = high = mean
    else:
        places = [sum((texel[c] - mean[c]) * axis[c] for c in range(4)) / length for texel in texels]
        low = [mean[c] + axis[c] * min(places) for c in range(4)]
        high = [mean[c] + axis[c] * max(places) for c in range(4)]

    # A block opaque throughout keeps the shared bit set, so its alpha decodes to 255 rather than 254
    # where the color alone would have chosen the bit clear, and an opaque texture reads opaque.
    shared = (1,) if all(texel[3] == 255 for texel in texels) else (0, 1)
    endpoints = quantize(low, shared), quantize(high, shared)
    indices = bc7_indices(texels, endpoints)

    # Fitted again by least squares to the indices found, kept where it lessens the error.
    refit = least_squares(texels, indices)
    if refit is not None:
        others = quantize(refit[0], shared), quantize(refit[1], shared)
        other_indices = bc7_indices(texels, others)
        if bc7_error(texels, others, other_indices) < bc7_error(texels, endpoints, indices):
            endpoints, indices = others, other_indices

    (q0, p0), (q1, p1) = endpoints
    if indices[0] >= 8:
        q0, q1, p0, p1 = q1, q0, p1, p0
        indices = [15 - index for index in indices]

    bits = 1 << 6
    shift = 7
    for c in range(4):
        bits |= q0[c] << shift
        bits |= q1[c] << (shift + 7)
        shift += 14
    bits |= p0 << shift | p1 << (shift + 1)
    shift += 2
    bits |= indices[0] << shift
    shift += 3
    for index in indices[1:]:
        bits |= index << shift
        shift += 4
    return bits.to_bytes(16, "little")


def quantize(endpoint, bits=(0, 1)):
    """An endpoint's seven bits a channel and the bit they share, the pair nearest it of the bits allowed."""
    best = None
    for bit in bits:
        values = [max(0, min(127, int((max(0.0, min(255.0, c)) - bit) / 2 + 0.5))) for c in endpoint]
        error = sum(((value << 1 | bit) - c) ** 2 for value, c in zip(values, endpoint))
        if best is None or error < best[0]:
            best = (error, values, bit)
    return best[1], best[2]


def expand(endpoint):
    values, bit = endpoint
    return [value << 1 | bit for value in values]


def bc7_indices(texels, endpoints):
    c0, c1 = expand(endpoints[0]), expand(endpoints[1])
    d = [b - a for a, b in zip(c0, c1)]
    dd = sum(value * value for value in d)
    if dd == 0:
        return [0] * 16
    return [NEAREST[max(0, min(64, int(sum((texel[c] - c0[c]) * d[c] for c in range(4)) * 64 / dd + 0.5)))] for texel in texels]


def bc7_error(texels, endpoints, indices):
    c0, c1 = expand(endpoints[0]), expand(endpoints[1])
    error = 0
    for texel, index in zip(texels, indices):
        w = WEIGHTS[index]
        for c in range(4):
            error += (((64 - w) * c0[c] + w * c1[c] + 32 >> 6) - texel[c]) ** 2
    return error


def least_squares(texels, indices):
    """The endpoints that best give the texels at the weights the indices name, or nothing where they are all one."""
    a00 = a01 = a11 = 0.0
    b0 = [0.0] * 4
    b1 = [0.0] * 4
    for texel, index in zip(texels, indices):
        t = WEIGHTS[index] / 64.0
        s = 1.0 - t
        a00 += s * s
        a01 += s * t
        a11 += t * t
        for c in range(4):
            b0[c] += s * texel[c]
            b1[c] += t * texel[c]
    determinant = a00 * a11 - a01 * a01
    if abs(determinant) < 1e-9:
        return None
    return ([(a11 * b0[c] - a01 * b1[c]) / determinant for c in range(4)],
            [(a00 * b1[c] - a01 * b0[c]) / determinant for c in range(4)])


def bc5(image):
    """The image's red and green in BC5, each a BC4 block of its own."""
    out = bytearray()
    for block in texel_blocks(image.convert("RGB"), 2):
        out += bc4_block([texel[0] for texel in block])
        out += bc4_block([texel[1] for texel in block])
    return bytes(out)


def bc4_block(values):
    """One channel's block in BC4's eight-step mode, its highest value first."""
    high, low = max(values), min(values)
    bits = high | low << 8
    if high != low:
        for i, value in enumerate(values):
            step = int((value - low) * 7 / (high - low) + 0.5)
            index = 0 if step == 7 else 1 if step == 0 else 8 - step
            bits |= index << (16 + 3 * i)
    return bits.to_bytes(8, "little")


def bc4_palette(block):
    high, low = block[0], block[1]
    return [high, low] + [((8 - i) * high + (i - 1) * low + 3) // 7 for i in range(2, 8)]


def psnr(errors, count):
    return 99.0 if errors == 0 else 10 * math.log10(255 * 255 * count / errors)


def psnr_bc7(image, blocks):
    """The top level's error against its blocks, decoded as mode 6 decodes, in decibels."""
    total = 0
    count = 0
    for at, texels in enumerate(texel_blocks(image.convert("RGBA"), 4)):
        bits = int.from_bytes(blocks[16 * at:16 * at + 16], "little")
        shift = 7
        c0, c1 = [], []
        for _ in range(4):
            c0.append(bits >> shift & 127)
            c1.append(bits >> (shift + 7) & 127)
            shift += 14
        p0, p1 = bits >> shift & 1, bits >> (shift + 1) & 1
        shift += 2
        c0 = [value << 1 | p0 for value in c0]
        c1 = [value << 1 | p1 for value in c1]
        indices = [bits >> shift & 7]
        shift += 3
        for _ in range(15):
            indices.append(bits >> shift & 15)
            shift += 4
        for texel, index in zip(texels, indices):
            w = WEIGHTS[index]
            for c in range(4):
                total += (((64 - w) * c0[c] + w * c1[c] + 32 >> 6) - texel[c]) ** 2
            count += 4
    return psnr(total, count)


def psnr_bc5(image, blocks):
    total = 0
    count = 0
    for at, texels in enumerate(texel_blocks(image.convert("RGB"), 2)):
        for channel in range(2):
            block = blocks[16 * at + 8 * channel:16 * at + 8 * channel + 8]
            palette = bc4_palette(block)
            bits = int.from_bytes(block, "little") >> 16
            for i, texel in enumerate(texels):
                total += (palette[bits >> (3 * i) & 7] - texel[channel]) ** 2
                count += 1
    return psnr(total, count)


# The file.

def ktx2(format, levels, blocks):
    """
    A KTX2 file of the levels' blocks as they are, the largest first in the index and last in the
    file, each level at a multiple of a block's sixteen bytes, as the format asks of levels kept as
    they are.
    """
    width, height = levels[0].size
    descriptor = data_format(format)
    pairs = [(b"KTXwriter", b"build/textures.py")]
    key_values = b""
    for key, value in pairs:
        entry = key + b"\0" + value + b"\0"
        key_values += struct.pack("<I", len(entry)) + entry
        key_values += b"\0" * (-len(key_values) % 4)

    header_size = 12 + 9 * 4 + 4 * 4 + 2 * 8
    index_size = 24 * len(levels)
    descriptor_at = header_size + index_size
    key_values_at = descriptor_at + len(descriptor)
    data_at = key_values_at + len(key_values)

    # The levels' bytes from the smallest to the largest, as the format lays them out.
    offsets = [0] * len(levels)
    at = data_at
    for level in reversed(range(len(levels))):
        at += -at % 16
        offsets[level] = at
        at += len(blocks[level])

    out = bytearray(b"\xabKTX 20\xbb\r\n\x1a\n")
    out += struct.pack("<9I", format, 1, width, height, 0, 0, 1, len(levels), 0)
    out += struct.pack("<4I", descriptor_at, len(descriptor), key_values_at, len(key_values))
    out += struct.pack("<2Q", 0, 0)
    for level in range(len(levels)):
        out += struct.pack("<3Q", offsets[level], len(blocks[level]), len(blocks[level]))
    out += descriptor
    out += key_values
    for level in reversed(range(len(levels))):
        out += b"\0" * (offsets[level] - len(out))
        out += blocks[level]
    return bytes(out)


def data_format(format):
    """The data format descriptor of a block format, its total size first and its one basic block."""
    if format == BC5_UNORM:
        model, transfer = MODEL_BC5, TRANSFER_LINEAR
        samples = [(0, 63, 0), (64, 63, 1)]
    else:
        model, transfer = MODEL_BC7, TRANSFER_SRGB if format == BC7_SRGB else TRANSFER_LINEAR
        samples = [(0, 127, 0)]
    block_size = 24 + 16 * len(samples)
    block = struct.pack("<II", 0, 2 | block_size << 16)
    block += struct.pack("<4B", model, 1, transfer, 0)
    block += struct.pack("<4B", 3, 3, 0, 0)
    block += struct.pack("<8B", 16, 0, 0, 0, 0, 0, 0, 0)
    for offset, length, channel in samples:
        block += struct.pack("<HBB4BII", offset, length, channel, 0, 0, 0, 0, 0, 0xFFFFFFFF)
    return struct.pack("<I", 4 + len(block)) + block


if __name__ == "__main__":
    sys.exit(main())

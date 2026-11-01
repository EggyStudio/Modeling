# Modeling

Modeling is a library both engines, 3DEngine and BevyCSharp, take as a git submodule, for the edit
mesh shaped by operations through a selection, its recipes and the `model.*` commands. It references
no engine, and each engine implements the interfaces it declares where it binds the module.

## Taking it into an engine

An engine adds the repository as a git submodule under `modules/` and references its project, here
from a project one folder below the engine's root.

```bash
git submodule add https://github.com/EggyStudio/Modeling.git modules/Modeling
```

```xml
<ProjectReference Include="..\modules\Modeling\Modeling\Modeling.csproj" />
```

A clone of the engine fetches the module with `git clone --recurse-submodules`, or with
`git submodule update --init` in a clone made without it, and a workflow checks it out with
`submodules: true` on `actions/checkout`. A change the engine uses is committed and pushed here
before the engine's commit that moves its pointer, so the engine's history never names a commit
this repository does not have.

## Building and testing

With the .NET 10 SDK:

```bash
dotnet build Modeling.slnx
dotnet test Modeling.Tests
```

## Textures

`Modeling/Textures` holds interior and architectural texture sets, each three KTX2 files with their
mipmaps in the formats of BevyCSharp's vegetation collection, which a GPU samples as they are.

| File | Channels | Encoding | Size |
|---|---|---|---|
| `albedo.ktx2` | color in RGB, opacity in A | BC7, sRGB | the set's |
| `normal.ktx2` | the tangent-space normal's X and Y in RG | BC5 | half the albedo's |
| `surface.ktx2` | occlusion in R, roughness in G, metallic in B, translucency in A | BC7, linear | half the albedo's |

| Set | Maker | Albedo | Files |
|---|---|---|---|
| `fleck-carpet` | Rohner | 1024 by 1024 | 1,365, 341 and 341 KB |
| `chevron-wallpaper` | RegularlyBlue | 512 by 1024 | 683, 171 and 171 KB |

The collection holds two sets in six files, 3.0 MB together, as `build/textures.py` writes their
sizes into the manifest. A set is at most 1024 square and the collection at most 32 MB, which
`dotnet test Modeling.Tests` holds, along with each set's channels decoded as a GPU decodes them.
The levels are kept without the zstd BevyCSharp's collection puts over them, since .NET's library
has none, so a reader in C# takes the files with no package added.

`textures.json` beside the sets is the recipe of each, its source files under `.ref/`, which the
repository leaves out, its size, its maps and what each channel takes, and `build/textures.py`
builds the sets from it the same byte for byte, with Python 3 and Pillow.

```bash
build/textures.py                      # build every set whose source is under .ref/
build/textures.py chevron-wallpaper    # build one
```

Neither source has a roughness map, so each recipe gives one roughness to the whole set, 0.95 for
the carpet and 0.8 for the paper, and the wallpaper's normal is flat, as a color scan holds no
relief. The carpet's normal map says nothing of which way its green points and is kept as it came,
and `flip_green` in its recipe turns it over. The wallpaper's scan does not meet itself at its
edges, so its set is built from its repeat, a half-drop of 4176 by 6243 of the scan's pixels that
`build/textures.py --repeat` found, drawn straight into 512 by 1024, each texel the mean of the
copies of its place the scan holds. A surface maps the tile to 17.7 by 26.4 cm, the size the
manifest gives from the scan's 600 dots an inch, so its texels are a third wider than they are tall.

## License

The Mozilla Public License 2.0, in [LICENSE](LICENSE).

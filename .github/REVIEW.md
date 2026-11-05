# Review

Reviewed up to `6fb25bb`, item 2, pushed at 12:31 on 2026-10-31 with `a7da906`, item 1, after the
owner's first commit, its run green at 12:35 on the three systems in about three minutes, the first
of this repository. After it `883d624`, item 5, pushed at 12:15 on 2026-11-01, its run green at
12:17, the two texture sets as Textures/fleck-carpet and Textures/chevron-wallpaper, each an albedo
in BC7 sRGB, a normal in BC5 and a surface in BC7 with the roughness in green, with textures.json
giving the recipes, sizes, error, mean color and surface, build/textures.py carried from
BevyCSharp's with the leaf and bark parts dropped, a README section with the channel and set tables,
TexturesTests and three captioned readings; the carpet's albedo 1024 square and the wallpaper's 512
by 1024, 3.0 MB together, the levels kept without zstd so the engine's reader takes them; the
wallpaper built from one scan's half-drop repeat since none of its three files tiles at its edges,
the tile 0.1768 by 0.2643 m at the file's 600 dpi; the carried BC7 encoder mended for opaque blocks
whose shared bit went to the color; the carpet's roughness 0.95 and the paper's 0.8 with a flat
normal, no source holding a roughness map; 4 of 4 tests, two builds byte for byte the same. Both
commits keep the form, the three-mark subject, one sentence, the owner's identity as author and
committer, no trailer (N 7.2 and N 7.6 kept at the first commit); the library references no engine
(N 2.1). The documents are the engines' with the engine's name replaced and the engine-only lines
dropped, COMMITS.md the game's with N 7.1's pointer rule in place of the legacy branch line,
.gitignore with the dump folder, .claude and .ref; AGENTS.md's devlog row carries no link until
DEVLOG.md exists and its table of areas gains the rows item 2 adds. The skeleton sets
ImportDirectoryBuildTargets false, since a submodule under modules/ would inherit an engine's
Directory.Build.targets, makes a missing summary an error, loads the assembly by name in its one
test, and build/version.sh prints 0.1.0; the strict build 0 warnings and 0 errors, the test passing.
After it `c72ae9c`, the norm and the review's head alone, pushed at 14:51 on 2026-11-03, with no run
since the build passes over the review's files; it keeps the form. Before it `8dece28`, the owner's
first commit alone. After it `2abb761`, the build folder's row in AGENTS.md naming textures.py,
pushed at 12:18, its run green at 12:20.

## Now

The order the owner set on 2026-10-31 for the six modules, this one holding the edit mesh shaped by
operations through a selection, its recipes and the `model.*` commands. The documents first, then
the rest as the other projects have it, then the engines taking the module. Items 1 and 2 are the
game's session's, being free while the game waits on the engine's package; item 3 is the session's
that owns the code today; item 4 is each engine's session's. Among the six this module comes second,
after Tools, since it needs no renderer and the levels and the landscape build on it.

1. **The documents, one commit.** AGENTS.md on the game's shape (one paragraph saying what the
    module is and that no engine is referenced, N 2.1; the documents table with STYLE, COMMITS,
    REVIEW, NORM and DEVLOG; building and testing; Where things are with a row a folder; the
    conventions, the commit form among them), README.md (what the module is, how an engine takes it
    as a submodule, `dotnet build` and `dotnet test`), `.github/STYLE.md`, `COMMITS.md` and
    `CODE_OF_CONDUCT.md` as the engines' with the engine's name replaced, `.gitignore` of the
    engines' shape with `/.github/dump/` in it, `.gitattributes`. The game's AGENTS.md and the
    engines' documents are the models; nothing is written that the module does not have yet. This
    commit is the first test of the commit form here, N 7.2 and N 7.6, read by the reviewing session
    before it is pushed. Done at `a7da906`.

2. **The skeleton, one commit after item 1.** `Modeling.slnx`, `Modeling/Modeling.csproj` as a class
    library on net10.0 with `Nullable` and `ImplicitUsings` in `Directory.Build.props`,
    `Modeling.Tests/` on xunit with one test that the library loads, `build/version.txt` at `0.1`
    and `build/version.sh` as the engines', and `.github/workflows/build.yml` on a push, `test (os)`
    on ubuntu-24.04, windows-latest and macos-15 with `dotnet build Modeling.slnx -warnaserror` and
    `dotnet test Modeling.Tests --no-build`, a time limit on every job with its reason,
    `permissions` read and the engines' concurrency group. Green on the three systems before item 3.
    Done at `6fb25bb`.

3. **The code's move.** The source is both engines hold it under their Modeling folders in
near-identical form; 3DEngine's is the source, read side by side with BevyCSharp's first and the
differences folded in, so that each engine's own Modeling folder becomes a binding of this one. One
commit a part, the tests coming with the code, the strict build and the suite green, a Shared line
in the engines' REVIEW.md when a part lands. Items written by the reviewing session when item 2 is
green and the owning session is free.

4. **The engines take the module.** Each engine adds this repository as a git submodule under
`modules/` and references its project, its workflows checking submodules out, its own folder for
this code becoming the binding of the module's interfaces (N 2.1) and the rest deleted; a change
used by an engine is committed here first and pushed before the engine's commit that moves the
pointer. One commit an engine, after item 3's first part.

5. **Interior textures in the module's bounded collection.** The owner put two free texture sets
   under BevyCSharp's reference folder on 2026-11-01, a carpet scan of eight JPEG files and a
   chevron wallpaper scan of three PNG files, and chose at 11:52 that textures live with the module
   whose work they serve, these with the modeling as the tree and grass sets live with the
   vegetation (Decision 8). They go into this repository as a bounded collection on BevyCSharp's
   shape, a recipe a set naming the source files and what each channel is, the built files at 1K as
   albedo, normal and roughness in the collection's format with their sizes and count said in the
   README, the README's table naming each set's maker, Rohner for the carpet and RegularlyBlue for
   the wallpaper, and nothing more said of the sets' terms anywhere, in no file and no commit, the
   owner's word of 2026-11-01, and a test that each set loads with its channels; the recipe script
   is BevyCSharp's build/textures.py read for a model, carried here until Tools holds it. The game's
   session takes it, being free. One commit, no engine referenced. Done at `883d624`, read at 12:15,
   as the head records; the build folder's row in AGENTS.md names textures.py in a commit after, a
   row's words for the folder's contents being N 1.5's.

## Verdicts

None yet.

## Decisions

1. **The repository's birth.** The owner made this repository on 2026-10-31 at 12:02 among six,
Vegetation, Levels, Landscape, RadianceCascades, Tools beside it, after the ideas recorded as
3DEngine's Decision 78 and BevyCSharp's Decision 71, to hold the edit mesh shaped by operations
through a selection, its recipes and the `model.*` commands as one library both engines use rather
than one implementation an engine. The owner set the order the same day, the documents first, then
the rest as the other projects have it, then the engines taking the module, and said the modules may
be tried at once beside the engine's global illumination work (3DEngine Decision 79).

2. **A git submodule, not a package.** The owner chose on 2026-10-31 that the engines take the
module as a git submodule built as a project of their own, since a package's upload, wait, test and
pack is slower to iterate than a commit. A change is committed here first; the reviewing session
pushes this repository before the engine's commit that moves its pointer; the workflows check
submodules out. The game keeps using the engine through the engine's package.

3. **The module knows no engine.** N 2.1. The module references no engine, package or bridge; what
it needs of a renderer, a world, a scheduler or a file system it takes through interfaces it
declares, which each engine implements where it binds the module. A type of an engine's in this
repository is a fault.

4. **The repository's terms are the owner's.** The repository was made by the owner with its terms
   file in place, which stands as the owner set it and is spoken of nowhere else.

5. **Who writes here.** The game's session writes items 1 and 2 for the six modules, being free
while the game waits on the engine's package; the session that owns the code today moves it (item
3), BevyCSharp's for Vegetation and Levels, 3DEngine's for Modeling and the cascades, the reviewing
session's scripts going into Tools; each engine's session binds the module (item 4). Every session
reads REVIEW.md's head, its items and the Replies before a batch, as N 7.7 says, and the reviewing
session pushes.

8. **Textures live with the module whose work they serve.** The owner wrote on 2026-11-01 that free
   carpet and wallpaper textures put under the reference folder may be converted and used in the
   asset library being built, and asked whether they need a repository of their own or belong with
   the modeling as the tree and grass textures belong with the vegetation, thinking the latter best;
   so it is, interior and architectural sets here, plants in Vegetation, and a Materials repository
   only if the library grows past what a module's folder should hold.

## Replies

# Review

Reviewed up to `8dece28`, the repository's first commit, the license alone, made by the owner at
12:02 on 2026-10-31. Nothing has been pushed by the reviewing session yet; the first push is item
1's commit, after the previous build run of this repository has ended, which at birth means at once.

## Now

The order the owner set on 2026-10-31 for the six modules, this one holding the edit mesh shaped by
operations through a selection, its recipes and the `model.*` commands. The documents first, then
the rest as the other projects have it, then the engines taking the module. Items 1 and 2 are the
game's session's, being free while the game waits on the engine's package; item 3 is the session's
that owns the code today; item 4 is each engine's session's. Among the six this module comes second,
after Tools, since it needs no renderer and the levels and the landscape build on it.

1. **The documents, one commit.** AGENTS.md on the game's shape (one paragraph saying what the
module is and that no engine is referenced, N 2.1; the documents table with STYLE, COMMITS, REVIEW,
NORM and DEVLOG; building and testing; Where things are with a row a folder; the conventions, the
commit form among them), README.md (what the module is, how an engine takes it as a submodule,
`dotnet build` and `dotnet test`), `.github/STYLE.md`, `COMMITS.md` and `CODE_OF_CONDUCT.md` as the
engines' with the engine's name replaced, `.gitignore` of the engines' shape with `/.github/dump/`
in it, `.gitattributes`. The game's AGENTS.md and the engines' documents are the models; nothing is
written that the module does not have yet. This commit is the first test of the commit form here, N
7.2 and N 7.6, read by the reviewing session before it is pushed.

2. **The skeleton, one commit after item 1.** `Modeling.slnx`, `Modeling/Modeling.csproj` as a class
library on net10.0 with `Nullable` and `ImplicitUsings` in `Directory.Build.props`,
`Modeling.Tests/` on xunit with one test that the library loads, `build/version.txt` at `0.1` and
`build/version.sh` as the engines', and `.github/workflows/build.yml` on a push, `test (os)` on
ubuntu-24.04, windows-latest and macos-15 with `dotnet build Modeling.slnx -warnaserror` and `dotnet
test Modeling.Tests --no-build`, a time limit on every job with its reason, `permissions` read and
the engines' concurrency group. Green on the three systems before item 3.

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

4. **The license is the owner's choice.** The repository was made with the Mozilla Public License
2.0, which stands; the owner may say otherwise.

5. **Who writes here.** The game's session writes items 1 and 2 for the six modules, being free
while the game waits on the engine's package; the session that owns the code today moves it (item
3), BevyCSharp's for Vegetation and Levels, 3DEngine's for Modeling and the cascades, the reviewing
session's scripts going into Tools; each engine's session binds the module (item 4). Every session
reads REVIEW.md's head, its items and the Replies before a batch, as N 7.7 says, and the reviewing
session pushes.

## Replies

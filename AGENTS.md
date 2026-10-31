# Modeling

Modeling is a library both engines, 3DEngine and BevyCSharp, take as a git submodule, for the edit
mesh shaped by operations through a selection, its recipes and the `model.*` commands. It references
no engine, no engine's package and no engine's bridge (NORM.md, N 2.1). What it needs of a renderer,
a world, a scheduler or a file system it takes through an interface it declares, which each engine
implements where it binds the module.

## Documents

| File | Holds |
|---|---|
| [README.md](README.md) | What the module is, how an engine takes it as a submodule, and how it is built and tested |
| [.github/STYLE.md](.github/STYLE.md) | Rules for every comment, message and Markdown file |
| [.github/COMMITS.md](.github/COMMITS.md) | How and when work is committed |
| [.github/REVIEW.md](.github/REVIEW.md) | Direction from the reviewing session, which comes before any other order of work |
| [.github/NORM.md](.github/NORM.md) | The numbered rules the module keeps, each with what checks it, the same text in the six module repositories |
| `DEVLOG.md` | What landed by day, with the pictures `.github/assets/readings` keeps, generated from them and the history |

## Building and testing

```bash
dotnet build Modeling.slnx
dotnet test Modeling.Tests
```

The tests need no window and no GPU. The build workflow builds with warnings failing the build and
runs the tests on Linux, Windows and macOS on every push (NORM.md, N 6.1 and N 6.2).

## Where things are

| Path | Holds |
|---|---|
| `.github` | The documents above but the README, and the build workflow |
| `Modeling` | The library, `Modeling.csproj` |
| `Modeling.Tests` | The xunit tests of the library |
| `build` | The version, `version.txt`'s major and minor set by hand and `version.sh`, which prints it with the patch counted from the history |

## Conventions

- Comments explain **why**, in prose. Match the surrounding density rather than trimming them.
- Every public type and member carries an XML summary, with a `<remarks>` section where there is
  reasoning or a trap to record, and the library's build stops where one is missing.
- A type, package or project of an engine's in the module's code or project files is the fault
  N 2.1 names. What the module needs of an engine is an interface it declares.
- Prose in this repository follows `.github/STYLE.md`, which governs comments, XML documentation,
  messages and Markdown. Read it before writing any of them.
- Each finished batch of work is committed on `main` locally and never pushed from here, since the
  reviewing session pushes `main` once the previous build run has ended, with a message whose
  subject is three invisible marks and whose description is one plain sentence. Before each commit,
  `.github/STYLE.md` is read and applied to what is staged, the message included.
  `.github/COMMITS.md` has the exact form, that pass, and how to split a batch that shares a file
  with another.
- A change an engine uses is committed here first, and the reviewing session pushes it before the
  engine's commit that moves the engine's pointer to it (N 7.1).
- `.github/REVIEW.md`'s head, the items of the batch and the Replies are read before a batch is
  started and before each commit. A second session writes it after reading the code and the
  history, and its Now list comes before any other order of work. Only its Replies section is
  edited here, for an item that is disputed, blocked or done, and the file is committed with
  whichever batch comes next.
- `.github/NORM.md` holds the rules the module keeps, each with a number, a reason and what checks
  it, and is written by the session that writes REVIEW.md. A rule read as wrong, or a fault of a
  kind no rule names, is said with a line under Replies in REVIEW.md beginning `Rule:`. A row that
  the table under Where things are lacks is added here when N 1.5 asks for it, and nothing else in
  this file changes without the owner's word (N 7.4).
- Every picture made while working goes as captured into `.github/dump/<date>/`, which git
  ignores, with a line in that day's `captions.md` (N 4.10), and the devlog's chosen ones go into
  `.github/assets/readings/` (N 4.8).

# Fluffpkg

The Fluffy, Multipurpose Package Manager :3

---

Woah, a package manager!
This is mostly just a fun project to play around, though I will likely use myself to simplify installations.

Right now it's lacking a lot of features: uninstall, modify, upgrade, etc... but these should be coming soon!

I run Debian, and that is where my testing is done. If you encounter any errors, feel free to file issues or pull requests!

## Installation and Updates

Simply clone (or download) the repo and link the python script to your path:

For example:

```
(cd into the folder you want to install the source into)
git clone https://github.com/Thawnyrose/fluffpkg
ln -s ~/Applications/fluffpkg/fluffpkg.py ~/.local/bin/fluffpkg
(If you want fluffpkg packages to be executable)
echo "export PATH=\"~/.fluffpkg/bin\":\$PATH" >> ~/.bashrc
```

To uninstall, delete the symlink at `~/.local/bin/fluffpkg` and remove the folder you installed the source into. It is HIGHLY recommended to first uninstall all packages installed by fluffpkg first, otherwise dangling files may be left such as broken launcer files, etc...

To update, simply got to the source folder and run `git fetch` to pull the newest source

## Commands

### install

```
Usage: install [--nolauncher] [--version = ] <packages...>
```

Searches through local sources for packages to install them.

### list

```
Usage: fluffpkg list [--installed]
```

Lists packages found in sources, or packages that are installed. Note that these come from different databases, and there's no guarantee an installed package is in the sources, or the other way round.

### upgrade

```
Usage: upgrade [--force] [packages...]
```

If the package is installed, checks for upgrades and applies them

### remove

```
Usage: fluffpkg remove <packages...>
```

If the package is installed, uninstalls it

### modify

```
Usage: modify <package> <attribute> ...
Attributes:
  add-launcher           Add a launcher entry for the package
  remove-launcher        Remove the launcher entry for the package
  add-categories         Add categories to the launcher entry
  remove-categories      Remove categories from the launcher entry
```

Applies the given modification

### versions

```
Usage: fluffpkg versions <package>
```

Lists all versions available for installation

## Included Modules

### github-appimage

#### Provided Commands

```
add-github-appimage <owner/repo...>
```

Adds the given repo to the local sources

```
install-github-appimage <owner/repo...>
```

Adds the given repo to the local sources, and installs it

#### Installation

Uses Github's API to find the most recent release (not pre-release), then searches through the assets to find an appimage. If there are multiple, it tries to filter by system architecture.

## Module API

Example:

```
moduleLib.register(
    "github-appimage",
    {
        "install": install,
        "remove": remove,
        "upgrade": upgrade,
        "versions": versions,
        "commands": [
            (
                Command(
                    "add-github-appimage",
                    "Adds installation candidates for github appimages",
                    [PosArgs("owner/repo")],
                ),
                add_cmd,
            ),
            (
                Command(
                    "install-github-appimage",
                    "Adds and installs github appimages",
                    [
                        FlagArg("-l", "--nolauncher", "Don't install .desktop files"),
                        ValueArg("-v", "--version", "Specify a version for installation"),
                        PosArgs("owner/repo"),
                    ],
                ),
                add_install_cmd,
            ),
        ],
    },
)
```

```
install(candidate: Candidate, cmd_args: dict)
remove(installation: Installation, cmd_args: dict)
upgrade(installation: Installation, cmd_args: dict)
versions(installation: Installation, cmd_args: dict)

add_cmd(cmd_args: dict)
remove_cmd(cmd_args: dict)
add_install_cmd(cmd_args: dict)
```

## To-Do

- [ ] .deb sources

- [ ] Add remote source

- [ ] Remove remote source

- [ ] Maybe: Case sensitive categories

- [x] Support path in appimage

- [x] get-exec-path command

- [x] Fix help for advanced show and modify commands

- [x] user_pick to general

- [x] appimage source filtering

- [x] Remove unused 'categories' column from 'installs' table

- [x] Better docs (marginally, at least...)

- [x] If the source is manual and you manipulate categories, you should also do so for their installation candidates for updates

- [x] Add modify target for 'list-categories'?

- [x] Better format help

- [x] Better argument system

- [x] Fix new argument system to also support module

- [x] List versions of a file

- [x] Install specific version

- [x] Version lock

- [x] Dynamic Modules

- [x] Databases instead of json!
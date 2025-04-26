# Fluffpkg

The Fluffy, Multipurpose Package Manager :3

---

Woah, a package manager!
This is mostly just a fun project to play around, though I will likely use myself to simplify installations.

Right now it's lacking a lot of features: uninstall, modify, upgrade, etc... but these should be coming soon!

I run Debian, and that is where my testing is done. If you encounter any errors, feel free to file issues or pull requests!

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
        "commands": {
            "add-github-appimage": add_cmd,
            "install-github-appimage": add_install_cmd,
        },
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

- [ ] Better docs

- [x] If the source is manual and you manipulate categories, you should also do so for their installation candidates for updates

- [x] Add modify target for 'list-categories'?

- [x] Better format help

- [x] Better argument system

- [x] Fix new argument system to also support module
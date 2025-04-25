# Fluffpkg

The Fluffy, Multipurpose Package Manager :3

---

Woah, a package manager!
This is mostly just a fun project to play around, though I will likely use myself to simplify installations.

Right now it's lacking a lot of features: uninstall, modify, upgrade, etc... but these should be coming soon!

I run Debian, and that is where my testing is done. If you encounter any errors, feel free to file issues or pull requests!

## Commands

### install

`usage: fluffpkg install [--nolauncher] [--path] <packages...>`


Searches through local sources for packages to install them.

### list

`usage: fluffpkg list \[--installed\]`


Lists packages found in sources, or packages that are installed. Note that these come from different databases, and there's no guarantee an installed package is in the sources, or the other way round.

### upgrade

`usage: fluffpkg upgrade <packages...>`


If the package is installed, checks for upgrades and applies them


NYI

### remove

`usage: fluffpkg remove <packages...>`


If the package is installed, uninstalls it



### modify

`usage: fluffpkg modify <package> [add-launcher, remove-launcher, add-categories, remove-categories]`


Applies the given modification



## Included Modules

### github-appimage

#### Provided Commands

+ add-github-appimage
  
  `usage: fluffpkg add-github-appimage <owner/repo...>`
  
  
  Adds the given repo to the local sources

+ install-github-appimage
  
  `usage: fluffpkg install-github-appimage <owner/repo...>`
  
  
  Adds the given repo to the local sources, and installs it

#### Installation

Uses Github's API to find the most recent release (not pre-release), then searches through the assets to find an appimage. If there are multiple, it tries to filter by system architecture.

## Module API

```
# Example
moduleLib.register(
    "github-appimage",
    {
        "install": install,
        "remove": remove,
        "commands": {
            "add-github-appimage": add_cmd,
            "install-github-appimage": add_install_cmd,
        },
    },
)
```

```
install(candidate, nolauncher, path)
remove(installation)
command(args)
```

## To-Do

+ .deb sources
+ Better format help
+ Better docs
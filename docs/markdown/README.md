---
title: README
date: 2023-08-29
---

# `mssh-menu`


## Info

SSH into multiple devices from a single command, splitting the screen, and synchronize the keyboard input.

The devices are selected from a menu. This menu is generated from a CSV file the user creates.


## Overview

First, create a CSV file with the first column being the IP address or hostname of the device. Then create additional columns containing the tags which will end up being the groups.

Run `mssh-menu.py` by supplying the command and the name of the CSV file as the argument. 

For example, to run `mssh-menu.py` with the file `servers.csv` and both files are in the current directly, enter the following:

```bash
./mssh-menu.py servers.csv
```

By default, if no file is supplied, the script will look for a file named `servers.csv` in the user's home directory.

For a list of commands run `mssh-menu.py` with the `-h` or `--help` options.


## Screenshots

![Running the script and using the menu](https://raw.githubusercontent.com/toddwint/mssh-menu/main/docs/figures/mssh-menu.py.1.png)

![Logged into multiple devices and typing the same commands once](https://raw.githubusercontent.com/toddwint/mssh-menu/main/docs/figures/mssh-menu.py.2.png)


## Requirements

The following are requirements to run this script:

- python3
- ssh
- tmux


## Sample `servers.csv` file

```
host,tags,,,,
server1,Site 1 servers,,Odd numbered servers,,All servers
server2,Site 1 servers,,,Even numbered servers,All servers
server3,,Site 2 servers,Odd numbered servers,,All servers
server4,,Site 2 servers,,Even numbered servers,All servers
```

Or in human readable form:


| host    | tags           |                |                      |                       |             |
|---------|----------------|----------------|----------------------|-----------------------|-------------|
| server1 | Site 1 servers |                | Odd numbered servers |                       | All servers |
| server2 | Site 1 servers |                |                      | Even numbered servers | All servers |
| server3 |                | Site 2 servers | Odd numbered servers |                       | All servers |
| server4 |                | Site 2 servers |                      | Even numbered servers | All servers |


## TMUX defaults

Here is my default `.tmux.conf` file for reference.

This script will automatically take care of setting the `base-index` and `pane-base-index` to 1.

It will not configure the `default-terminal`, `history-limit`, or `mouse` options.

```
# Improve colors
set -g default-terminal screen-256color

# Set scrollback buffer to 10000
set -g history-limit 10000

# Enable mouse mode (tmux 2.1 and above)
set -g mouse on

# Set first windows and pane to index of 1 (instead of zero)
set -g base-index 1
set -g pane-base-index 1
```

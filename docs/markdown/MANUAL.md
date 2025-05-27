---
title: MSSH-MENU
section: 1
header: User Commands
footer: mssh-menu 0.0.6
date: 2025-05-23
author: Todd Wintermute
---


# Name

mssh-menu - Use CSV file with tags to ssh into multiple devices


# Synopsis

**`mssh-menu`** \[**`-h`**\] \[**`--completion`** {**`bash,zsh,fish`**}\] \[**`-v`**\] \[**`-n`** _`number`_\] \[**`-u`** _`user`_\] \[**`-c`** _`columns`_\] \[**`-m`**\] \[_`FILENAME.CSV`_\]


# Description

Input a CSV file that has a list of host and tags (multiple columns of tags are OK). This script will display to the user a list of groups by tag name and prompt for a selection of one or more items. The selection will launch multiple ssh connections all inside one `tmux` window with the keyboard synchronized. `ssh` and `tmux` are required to be available on the system path.


## Positional Arguments

___`FILENAME.CSV`___
: name of CSV file (default=$HOME/servers.csv)


## Option Flags

**`-h`**, **`--help`**
: show this help message and exit


**`-v`**, **`--version`**
: show the version number and exit


**`-n`** _`number`_, **`--number`** _`number`_
: **Risky option** Enter selection number or numbers (separated by commas and/or using a dash to specify a range) instead of showing the menu.


**`-u`** _`user`_, **`--user`** _`user`_
: Enter a username instead of being prompted for one.


**`-c`** _`columns`_, **`--columns`** _`columns`_
: Override the autocalculation of menu columns. Specify an maximum number of menu columns to display.


**`-m`**, **`--menu-only`**
: Display the menu selection list and exit.


## Shell Completion Options

**`--completion`** {**`bash,zsh,fish`**}
: Print mssh-menu shell completion to the terminal and exit


# Examples


## Sample `servers.csv` file

The examples use the following tags list:

| host    | tags   |           |     |
|---------|--------|-----------|-----|
| server1 | Site 1 | Primary   | All |
| server2 | Site 1 | Redundant | All |
| server3 | Site 2 | Primary   | All |
| server4 | Site 2 | Redundant | All |


Here is the data in CSV format. Save this file as `servers.csv`. You can edit it in a spreadsheet program like Microsoft Excel or LibreOffice Calc. You can also edit it using a simple text editing program like Notepad.

```
host,tags,,
server1,Site 1,Primary,All
server2,Site 1,Redundant,All
server3,Site 2,Primary,All
server4,Site 2,Redundant,All
```

Note: The SSH connections will be in the order of the items in the CSV file.


## Example 1

Log into all the odd numbered servers.

```
$ mssh-menu examples/servers.csv
```

A menu appears. Select the option corresponding to **"2. Primary"**.

Enter a username. The same username will be used on all servers.

The output should look like this:

```
1. All      
2. Primary  
3. Redundant
4. Site 1   
5. Site 2   
Info: Use commas to separate multiple entries and dash for ranges.
Select one or more numbers from the list [1-5,q] (default=none): 2
Selected: `2. Primary`
server1
server3 

Enter username (default=none): admin
```

A window opens with two panes and an ssh connection is established to both servers (admin@server1 and admin@server3).



## Example 2

Log into all the servers at Site 2.

```
$ mssh-menu examples/servers.csv
```

A menu appears. Select the option corresponding to **"5. Site 2"**.

Enter a username. The same username will be used on all servers.

```
1. All      
2. Primary  
3. Redundant
4. Site 1   
5. Site 2   
Info: Use commas to separate multiple entries and dash for ranges.
Select one or more numbers from the list [1-5,q] (default=none): 5
Selected: `5. Site 2`
server3
server4 

Enter username (default=none): admin
```

A window opens with two panes and an ssh connection is established to both servers (admin@server3 and admin@server4).


## Example 3

Use the `--menu-only` option and `grep` to see which menu options correspond to the **redundant** servers.

```
$ mssh-menu examples/servers.csv --menu-only --columns 1 | grep -i redundant
```

The output should be:

```
3. Redundant
```


## Example 4

Use the menu number as an option to `mssh-menu` to ssh without using the menu.

Using the output from example 3, enter the following command.

```
$ mssh-menu examples/servers.csv --user admin --number 3
```

The menu is not displayed, and a window opens with two panes and an ssh connection is established to both servers (admin@server2 and admin@server4).
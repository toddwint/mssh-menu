#!/usr/bin/env python3
"""
Input a CSV file that has a list of host and tags
(multiple columns of tags are OK). This script will display to the user
a list of groups by tag name and prompt for a selection of
one or more items. The selection will launch multiple ssh connections
all inside one `tmux` window with the keyboard synchronized.
`ssh` and `tmux` are required to be available on the system path.
"""

__module__ = 'mssh_menu'
__script__ = 'mssh-menu'
__author__ = 'Todd Wintermute'
__version__ = '0.0.6'
__date__ = '2025-05-23'
__info__ = 'Use CSV file with tags to ssh into multiple devices'

import argparse
import csv
import datetime as dt
import importlib.resources
import json
import math
import pathlib
import re
import shutil
import subprocess
import sys


_jsoncache = pathlib.Path.home() / '.local/share/mssh-menu/mssh-menu.json'
_csv_default = pathlib.Path.home() / 'servers.csv'


def parse_arguments():
    """Create command line arguments and auto generated help"""
    from argparse import ONE_OR_MORE, OPTIONAL, ZERO_OR_MORE, SUPPRESS
    completion_parser = argparse.ArgumentParser(add_help=False)
    completion_group = completion_parser.add_argument_group(
        title='shell completion options',
        )
    completion_group.add_argument(
        '--completion',
        choices=['bash', 'zsh', 'fish'],
        help=f"Print {__script__} shell completion to the terminal and exit",
        )
    completion_args, _ = completion_parser.parse_known_args()
    parser=argparse.ArgumentParser(
        prog=__script__,
        description=__doc__,
        parents=[completion_parser],
        epilog='Please be responsible.',
        )
    parser.add_argument(
        '-v', '--version',
        help='show the version number and exit',
        action='version',
        version=f'Version: %(prog)s  {__version__}  ({__date__})',
        )
    parser.add_argument(
        '-n', '--number',
        type=str,
        help=(
            '**Risky option** '
            'Enter selection number or numbers (separated by commas and/or '
            'using a dash to specify a range) instead of showing the menu.'
            ),
        )
    parser.add_argument(
        '-u', '--user',
        type=str,
        help=f'Enter a username instead of being prompted for one.',
        )
    parser.add_argument(
        '-c', '--columns',
        type=int,
        default=None,
        help=(
            'Override the autocalculation of menu columns. '
            'Specify an maximum number of menu columns to display.'
            ),
        )
    parser.add_argument(
        '-m', '--menu-only',
        action='store_true',
        help='Display the menu selection list and exit.',
        )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        #help='Display the items passed to ssh via tmux; do not run it.',
        help=SUPPRESS, # Hidden option to print but not execute commands
        )
    parser.add_argument(
        'filename',
        metavar='FILENAME.CSV',
        type=pathlib.Path,
        default=_csv_default,
        nargs=OPTIONAL,
        help=f'name of CSV file (default=$HOME/servers.csv)',
        )
    return parser


def read_jsonfile(f=_jsoncache):
    """Takes a pathlib file path. Creates and returns a default json obj"""
    if (j := f).exists():
        jsonobj = json.loads(j.read_text())
    else:
        jsonobj = {}
    if not csvfile in jsonobj:
        jsonobj[csvfile] = {'user': '', 'last_selection': ''}
    return jsonobj


def write_jsonfile(jsonobj,f=_jsoncache):
    """Takes a jsonobj and a pathlib file path. Writes jsonobj to file.
    Returns the number of bytes written.
    """
    numbytes = f.write_text(
        json.dumps(jsonobj, indent=1),
        )
    return numbytes


def sortbydns(host):
    """Function which can be used as a key in sort to sort by dns name"""
    sort = host.split('.')[::-1]
    sort = sort[:2] + sort[-1:]
    return sort


def sortbycsv(host, csvlist):
    """Function which can be used as a key in sort to sort by order in csv"""
    sort = [item for item, *_ in csvlist].index(host)
    return sort


def natural_sort(somelist):
    """Takes a list of strings and sorts them in a natural human format
    also known as version sorting i.e. Number10 after Number1 and Number 2
    """
    l = somelist
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split(r'([0-9]+)',key)]
    return sorted(l, key=alphanum_key)


def open_csv(csv_filename):
    "Reads the CSV file and returns a list"
    # Open the csv file, remove empty lines and remove the header
    with csv_filename.open() as f:
        csvlist = [line for line in csv.reader(f) if line]
        _ = csvlist.pop(0)
    # Clean up the csvlist, remove whitespace & empties. Default tag if none
    csvlist = [
        (host.strip(), *([tag.strip() for tag in tags if tag] or ['No Tag']))
        for host, *tags in csvlist if host #checks for no host but tag exist
            ]
    return csvlist


def get_tags_from_csv(csvlist):
    "Returns a list of tags (tagslist) and a dictionary of tags (tagsdict)"
    # list of unique tags, (remove host and flatten the list, convert to set)
    tagslist = natural_sort(set([
        tag for tags in [rtags for host,*rtags in csvlist] for tag in tags
            ]))
    # initialize dictionary; keys are tag names; values are empty sets
    tagsdict = {tag: set() for tag in tagslist}
    # for each line, add the host to the tag key list if it contains the tag
    for host, *tags in csvlist:
        for tag in tagsdict:
            if tag in tags:
                tagsdict[tag].add(host)
    return tagslist, tagsdict


def horizontal_table(items, columns=1, sep='  '):
    """Takes a list. Returns a list of list per number columns given"""
    rows = math.ceil(len(items) / max(columns, 1))
    table = [items[(i*rows):(i*rows+rows)] for i in range(columns)]
    table = [g for g in table if g]
    return table[:-1] + [[item.removesuffix(sep) for item in table[-1]]]


def vertical_table(items, pad_lines=0, sep='  '):
    """Takes a list. Returns a list of list per number lines available"""
    lines = max(shutil.get_terminal_size().lines - max(pad_lines, 0), 1)
    columns = math.ceil(len(items) / lines)
    table = [items[(i*lines):(i*lines+lines)] for i in range(columns)]
    table = [g for g in table if g]
    return table[:-1] + [[item.removesuffix(sep) for item in table[-1]]]


def do_items_fit(table):
    """Takes a list of list. Determines if items will fit the term size"""
    widths = tuple(len(max(items, key=len)) for items in table)
    return sum(widths) <= shutil.get_terminal_size().columns


def optimal_number_of_columns(items, sep='  '):
    """Determines the maximum amount of columns that will fit on screen"""
    for n, _ in enumerate(items, 2):
        table = horizontal_table(items, n, sep)
        if not do_items_fit(table):
            return n-1


def format_items(items, sep='  '):
    """Adds a number before each item and a separator after"""
    d = len(str(len(items)))
    return [f"{n: >{d}}. {item}{sep}" for n, item in enumerate(items, 1)]


def format_table(table):
    """Takes a list of list. Returns a list of the text to print per line"""
    lengths = [len(row) for row in table]
    widths = tuple(len(max(items, key=len)) for items in table)
    table[-1].extend([''] * (max(lengths) - lengths[-1]))
    transposed_table = [list(row) for row in zip(*table)]
    tmp_table1 = [list(zip(row, widths)) for row in transposed_table]
    return [''.join([f"{i: <{w}}" for i, w in row]) for row in tmp_table1]


def make_table(items, columns=None, pad_lines=2, sep='  '):
    """Takes a list. Returns a list which will print neatly to the screen"""
    if columns:
        table = horizontal_table(items, columns, sep)
    else:
        table = vertical_table(items, pad_lines, sep)
        if not do_items_fit(table):
            columns = optimal_number_of_columns(items, sep)
            table = horizontal_table(items, columns, sep)
    return format_table(table)


def display_menu(tagslist, columns=None, pad_lines=0, sep='  '):
    """Displays a list of entries from csv file.
    Prompts user to make selection.
    Validates the selection and then returns it
    """
    if args.number:
        sel = parse_selection(args.number, len(tagslist))
        return sel
    l = format_items(tagslist, sep=sep)
    formatted_table = make_table(l, columns, pad_lines, sep)
    print('\n'.join(formatted_table))
    n = len(tagslist)
    if args.menu_only:
        sys.exit()
    default = ''
    j = read_jsonfile()
    if (d := j[csvfile]['last_selection']):
        default = ','.join(str(s) for s in d)
    message = '\n'.join([
        'Info: Use commas to separate multiple entries and dash for ranges.',
        f"Select one or more numbers from the list "
        f"[{f'1-{n}' if n>1 else '1'},q] (default={default or 'none'}): "
        ])
    try:
        sel = input(message) or default
    except KeyboardInterrupt:
        print(f"\n--> Keyboard interrupt pressed <--\nBye!")
        sys.exit(1)
    # Validate selection
    if sel.lower().startswith('q'):
        print('`q` pressed.\nProgram will now quit.\nBye.')
        sys.exit()
    elif sel == '':
        print('- - - - - - - - - -')
        print('No selection made. Try again')
        sel = display_menu(tagslist)
    else:
        sel = parse_selection(sel, n)
        if not sel:
            sel = display_menu(tagslist)
    j[csvfile]['last_selection'] = sel
    write_jsonfile(j)
    seltxt = ', '.join(f'`{l[int(i)-1].removesuffix(sep)}`' for i in sel)
    print(f'Selected: {seltxt}')
    return sel


def parse_selection(selection, n):
    """Takes a selection string and the max number of selections.
    Validates the input. Returns false if not valid. Else returns list.
    """
    selectlist = selection.replace(' ', '').split(',')
    tmplist = []
    for item in selectlist:
        if item.count('-') == 1:
            rangestart , rangeend = item.split('-')
            if (rangestart.isdecimal() and rangeend.isdecimal() and
                int(rangeend)+1 >= int(rangestart)):
                rangelist = range(int(rangestart), int(rangeend)+1)
                tmplist.extend(rangelist)
            else:
                print(f'Invalid input: `{item}`')
                return False
        elif item.isdecimal() and all((int(item)>0, int(item)<=n)):
            tmplist.append(int(item))
        else:
            print(f'Invalid input: `{item}`')
            return False
    return tmplist


def get_username():
    """Read last used username from json file. If modified, save new user"""
    if not args.user:
        default = ''
        j = read_jsonfile()
        if (d := j[csvfile]['user']):
            default = d
        message = f"Enter username (default={default or 'none'}): "
        try:
            user = input(message) or default
        except KeyboardInterrupt:
            print(f"\n--> Keyboard interrupt pressed <--\nBye!")
            sys.exit(1)
        j[csvfile]['user'] = user
        write_jsonfile(j)
    elif args.user:
        user = args.user
    else:
        print('Something is wrong.')
    return user


def send_list_to_ssh_or_display(sshaddrs, user):
    """Create the string of user@host entries provided to ssh via tmux"""
    if args.debug:
        sshlist = ' '.join(f'{user}@{h}' for h in sshaddrs)
        print(sshlist)
        return None
    else:
        rval = mssh_using_tmux(sshaddrs, user)
        return rval


def mssh_using_tmux(sshlist, user):
    """Creates a new tmux session using the supplied list of addresses"""
    now = dt.datetime.now().replace(microsecond=0)
    tstamp = now.isoformat().translate({ord('-'): '', ord(':'): ''})
    tmux_session = f'mssh-{tstamp}'
    window_name = ','.join(sshlist)
    rval = sh_run(f'tmux new-session -d -s "{tmux_session}"')
    rval = sh_run(f'tmux rename-window {tmux_session}')
    #rval = sh_run(f'tmux rename-window "{window_name}"')
    #rval = sh_run(f'tmux set-option -wg automatic-rename off')
    #rval = sh_run(f'tmux set-option -wg set-titles on')
    #rval = sh_run(f'tmux set-option -wg set-titles-string "mssh"')
    rval = sh_run(f'tmux set-option -wg status-left "[mssh] "')
    rval = sh_run(f'tmux set-option -wg status-left-length 24')
    rval = sh_run(f'tmux set-option -g pane-border-status top')
    rval = sh_run(f'tmux set-option -g pane-border-format " [ ###P #T ] "')
    rval = sh_run(f'tmux set-option -g base-index 1')
    rval = sh_run(f'tmux set-option -g pane-base-index 1')
    for item in sshlist:
        rval = sh_run(f"tmux split-window 'ssh {user}@{item}'")
        rval = sh_run(f'tmux select-pane -T "{item}"')
        rval = sh_run(f'tmux select-layout tiled')
    rval = sh_run(f'tmux kill-pane -t 1')
    rval = sh_run(f'tmux set-window-option synchronize-panes on')
    rval = sh_run(f'tmux select-layout tiled')
    rval = sh_run(f'tmux attach -t "{tmux_session}"')
    return rval


def sh_run(command):
    """Runs a shell command via subprocess.run. Return value is int"""
    rval = subprocess.run(command, shell=True)
    return rval.returncode


def print_completion(shell):
    """Read a completion file and print the output"""
    resource = f"shell-completions/{shell}/{__script__}"
    completions = importlib.resources.files(__module__).joinpath(resource)
    if completions.exists():
        print(completions.read_text())
    else:
        print('Completions file not found')
        sys.exit(1)


def main():
    """Start of main program"""
    global args
    global csvfile
    parser = parse_arguments()
    args = parser.parse_args()
    if (shell := args.completion):
        print_completion(shell)
        return
    columns = args.columns
    csv_filename = args.filename
    csvfile = str(args.filename.resolve())
    # Verify the system has ssh and tmux
    if not shutil.which('ssh'):
        print(
            "`ssh` is required but was not found. "
            "Obtain `ssh`, and ensure `ssh` is on the system path. Bye."
            )
        sys.exit()
    if not shutil.which('tmux'):
        print(
            "`tmux` is required but was not found. "
            "Obtain `tmux`, and ensure `tmux` is on the system path. Bye."
            )
        sys.exit()
    if not csv_filename.exists():
        parser.print_help()
        print(f"\n[ERROR]: `{csv_filename.name}` was not found. Bye.")
        sys.exit()
    _jsoncache.parent.mkdir(parents=True, exist_ok=True)
    csvlist = open_csv(csv_filename)
    tagslist, tagsdict = get_tags_from_csv(csvlist)
    selection = display_menu(tagslist, columns=columns, pad_lines=5)
    csvsort = lambda i: sortbycsv(i, csvlist)
    sshaddrs = set([
        item for group in selection
        for item in tagsdict[tagslist[int(group)-1]]
            ])
    sshaddrs = sorted(sshaddrs, key=csvsort)
    print('\n'.join(sshaddrs),'\n')
    user = get_username()
    rval = send_list_to_ssh_or_display(sshaddrs, user)
    print('Done!')


if __name__ == '__main__':
    main()

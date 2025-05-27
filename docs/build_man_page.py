#!/usr/bin/env python3
"""Create a man page from argparse parser in python script"""

__module__ = 'build_man_page'
__script__ = 'build_man_page'
__author__ = 'Todd Wintermute'
__version__ = '0.0.1'
__date__ = '2025-03-21'
__info__ = __doc__

import argparse
import importlib
import pathlib
import subprocess
import sys
import textwrap


def parse_arguments():
    """Creates a help menu and a parser to get cli arguments."""
    from argparse import ONE_OR_MORE, OPTIONAL, ZERO_OR_MORE, SUPPRESS
    parser = argparse.ArgumentParser(
        prog=__script__,
        description=__doc__,
        epilog='Have a great day!',
        )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f"%(prog)s: {__version__} ({__date__})",
        help='Show the version number and exit',
        )
    parser.add_argument(
        '-t', '--template',
        metavar='template.md',
        default='template.md',
        type=pathlib.Path,
        help='Specify the markdown template file. Default=template.md',
        )
    parser.add_argument(
        '-a', '--append',
        metavar='file.md',
        action='append',
        default=[],
        type=pathlib.Path,
        help='Append an additional markdown file to the end',
        )
    parser.add_argument(
        '-o', '--output',
        metavar='man.md',
        default='man.md',
        type=pathlib.Path,
        help='Specify the name of the output. Default=man.md',
        )
    parser.add_argument(
        'parser',
        help=(
            'The parser to import in the form module:parser. Hint: add dir '
            'to PYTHONPATH and export PYTHONPATH if needed.'
            ),
        )
    return parser


def sort_action_groups(parser):
    """Return sorted list of argparse action groups in usage order"""
    sorted_groups = []
    for group in parser._action_groups:
        title = group.title
        if title == 'positional arguments':
            positional = group
        elif title == 'options':
            options = group
        else:
            sorted_groups.append(group)
    sorted_groups.append(options)
    sorted_groups.append(positional)
    return sorted_groups


def get_pkg_module_and_parser(module_and_parser):
    """Import and get package info. Return package module and parser"""
    module, parser = module_and_parser.split(':')
    pkg_module = importlib.import_module(module)
    pkg_parser = getattr(pkg_module, parser)()
    return pkg_module, pkg_parser


def find_in_sublist(nested_list, item):
    """Return the index of an item in a nested list"""
    for sub_list in nested_list:
        if item in sub_list:
            return(nested_list.index(sub_list), sub_list.index(item))


def get_mutual(parser):
    """Return a nest list of mutually exclusive arguments"""
    mutual = []
    for m in parser._mutually_exclusive_groups:
        names = []
        for action in m._group_actions:
            if action.option_strings:
                names.append(action.option_strings[0])
            else:
                names.append(action.metavar or action.dest)
        mutual.append(names)
    return mutual


def gen_usage(pkg_parser):
    """Return the argparse usage info in markdown format"""
    mutual_excl = get_mutual(pkg_parser)
    usage_md = f"**`{pkg_parser.prog}`**"
    for action in pkg_parser._actions:
        if action.option_strings:
            positional = None
            option = action.option_strings[0]
        else:
            option = None
            positional = action.metavar or action.dest or None
        arg_md = positional or option
        if action.help == '==SUPPRESS==':
            continue
        if option:
            value = action.metavar or action.dest or None
            nargs = action.nargs
            if isinstance(nargs, int):
                arg_values = [rf"_`{x}`_" for x in [value]*nargs]
                arg_md = rf"**`{option}`** {' '.join(arg_values)}".strip()
            elif nargs in ['?']:
                arg_md = rf"**`{option}`** \[_`{value}`_\]"
            elif nargs in ['*']:
                arg_md = rf"**`{option}`** \[_`{value} ...`_\]"
            elif nargs in ['+']:
                arg_md = rf"**`{option}`** _`{value}`_ \[_`{value} ...`_\]"
            elif (choices := action.choices):
                arg_md = rf"**`{option}`** {{**`{','.join(choices)}`**}}"
            else: # nargs = None
                if value:
                    arg_md = rf"**`{option}`** _`{value}`_"
                else:
                    arg_md = rf"**`{option}`**"
            if (loc := find_in_sublist(mutual_excl, option)):
                sub, pos = loc
                if pos == 0:
                    for m in mutual_excl[sub][1:]:
                        arg_md = rf"{arg_md} `|` {m}"
                else:
                    usage_md = usage_md.replace(option, arg_md)
                    continue
            if not action.required:
                arg_md = rf"\[{arg_md}\]"
        if positional:
            value = action.metavar or action.dest or None
            nargs = action.nargs
            if nargs in [0]:
                arg_md = rf"[___`{positional}`___]"
            elif isinstance(nargs, int):
                arg_values = [rf"___`{x}`___" for x in [value]*nargs]
                arg_md = rf"{' '.join(arg_values)}".strip()
            elif nargs in ['?']:
                arg_md = rf"\[_`{positional}`_\]"
            elif nargs in ['*']:
                arg_md = rf"\[_`{positional} ...`_\]"
            elif nargs in ['+']:
                arg_md = rf"___`{positional}`___ \[_`{positional} ...`_\]"
            elif (choices := action.choices):
                arg_md = rf"{{___`{','.join(choices)}`___}}"
            else: # nargs = None
                arg_md = rf"___`{positional}`___"
                print(positional)
            if (loc := find_in_sublist(mutual_excl, option)):
                sub, pos = loc
                if pos == 0:
                    for m in mutual_excl[sub][1:]:
                        arg_md = rf"{arg_md} `|` {m}"
                else:
                    usage_md = usage_md.replace(option, arg_md)
                    continue
        usage_md = f"{usage_md} {arg_md}"
    return usage_md


def gen_options(pkg_parser):
    """Return the argparse options info in markdown format"""
    options_md = ""
    for group in pkg_parser._action_groups:
        if len(group._group_actions):
            options_md = f"{options_md}\n"
            title = group.title
            if title in ['options']:
                title = f"## Option Flags"
            else:
                title = f"## {title.title()}" #title() = string format
            options_md = f"{options_md}{title}\n"
        for action in group._group_actions:
            if action.help == '==SUPPRESS==':
                continue
            flags = []
            if action.option_strings:
                positional = None
                options = action.option_strings
            else:
                options = None
                positional = action.metavar or action.dest or None
            for option in options or []:
                value = action.metavar or action.dest or None
                nargs = action.nargs
                if isinstance(nargs, int):
                    arg_values = [rf"_`{x}`_" for x in [value]*nargs]
                    flags.append(
                        rf"**`{option}`** {' '.join(arg_values)}".strip()
                        )
                elif nargs in ['?']:
                    flags.append(rf"**`{option}`** \[_`{value}`_\]")
                elif nargs in ['*']:
                    flags.append(rf"**`{option}`** \[_`{value} ...`_\]")
                elif nargs in ['+']:
                    flags.append(
                        rf"**`{option}`** _`{value}`_ \[_`{value} ...`_\]"
                        )
                elif (choices := action.choices):
                    flags.append(
                        rf"**`{option}`** {{**`{','.join(choices)}`**}}"
                        )
                else: # nargs = None
                    if value:
                        flags.append(rf"**`{option}`** _`{value}`_")
                    else:
                        flags.append(rf"**`{option}`**")
            if positional:
                value = action.metavar or action.dest or None
                nargs = action.nargs
                if nargs in [0]:
                    flags.append(positional)
                elif isinstance(nargs, int):
                    arg_values = [rf"___`{x}`___" for x in [value]*nargs]
                    flags.append(rf"{' '.join(arg_values)}".strip())
                elif nargs in ['?']:
                    flags.append(rf"___`{positional}`___")
                elif nargs in ['*']:
                    flags.append(rf"___`{positional}`___")
                elif nargs in ['+']:
                    flags.append(rf"___`{positional}`___")
                elif (choices := action.choices):
                    flags.append(rf"{{___`{','.join(choices)}`___}}")
                else: # nargs = None
                    flags.append(rf"___`{positional}`___")
                    print(positional)
            option_md = ', '.join(flags)
            options_md = f"{options_md}\n"
            options_md = f"{options_md}{option_md}\n"
            options_md = f"{options_md}: {action.help}\n"
            options_md = f"{options_md}\n"
    return options_md


def main():
    global pkg_module, pkg_parser ### ERASE LATER (for debug globals) ###
    """Main entry point for the program"""
    parser = parse_arguments()
    args = parser.parse_args()
    pkg_module, pkg_parser = get_pkg_module_and_parser(args.parser)
    usage = gen_usage(pkg_parser)
    options = gen_options(pkg_parser)
    version = pkg_module.__version__ or 'no version'
    date = pkg_module.__date__ or 'no date'
    author = pkg_module.__author__ or 'no author'
    description = (
        ' '.join(textwrap.wrap(pkg_parser.description)).strip()
        or 'no description'
        )
    program = pkg_parser.prog or 'no name'
    title = pkg_parser.prog.upper() or 'NO NAME'
    info = (
        ' '.join(textwrap.wrap(pkg_module.__info__)).strip()
        or 'no info'
        )
    if args.template.exists():
        raw_template = args.template.read_text()
    else:
        raw_template = (
            '---\n'
            'title: {title}\n'
            'section: 1\n'
            'header: User Commands\n'
            'footer: {program} {version}\n'
            'date: {date}\n'
            'author: {author}\n'
            '---\n\n\n'
            '# Name\n\n{program} - {info}\n\n\n'
            '# Synopsis\n\n{usage}\n\n\n'
            '# Description\n\n{description}\n\n{options}\n'
            )
    template_md = raw_template.format_map(vars())
    for f in args.append:
        if f.exists():
            template_md += f.read_text()
    args.output.write_text(template_md.strip(), encoding='utf-8')
    return


if __name__ == '__main__':
    main()

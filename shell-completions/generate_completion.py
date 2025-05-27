#!/usr/bin/env python3
"""Generate a completion from python argparse for a supplied shell"""

__module__ = 'generate_completion'
__script__ = 'generate_completion'
__author__ = 'Todd Wintermute'
__version__ = '0.0.1'
__date__ = '2025-03-12'

import argparse
import importlib
import pathlib
import sys


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
        '-s', '--shell',
        choices=['fish'],
        required=True,
        dest='shells',
        action='append',
        help=f"The type of shell to generate completions.",
        )
    parser.add_argument(
        '-a', '--alias',
        metavar='alias_name',
        action='append',
        default=[],
        help=f"Add an additional program alias name to the completion file.",
        )
    parser.add_argument(
        '-o', '--output',
        metavar='file',
        type=pathlib.Path,
        help="Specify to save the completion to a file instead of stdout.",
        )
    parser.add_argument(
        'parser',
        help=(
            'The parser to import in the form module:parser. Hint: add dir '
            'to PYTHONPATH and export PYTHONPATH if needed.'
            ),
        )
    return parser


def fish_completion(pkg_parser, add_aliases):
    """Print a shell completion for fish shell"""
    template = [f"# Fish shell completion for {pkg_parser.prog}\n\n"]
    # First completion command turns off file completion
    # A pathlib.Path option or positional will reenable file completion
    complete = [f"complete --command {pkg_parser.prog}"]
    for alias in add_aliases:
        complete.append(f"--command {alias}")
    complete.append(f"--no-files")
    template.append(' '.join(complete))
    # Then add all the optional or positional parameters
    for action in pkg_parser._actions:
        options = action.option_strings
        complete = [f"complete --command {pkg_parser.prog}"]
        for alias in add_aliases:
            complete.append(f"--command {alias}")
        for option in sorted(options, key=len):
            if option.startswith('--'):
                complete.append(f"--long-option {option.strip('--')}")
            else:
                complete.append(f"--short-option {option.strip('-')}")
        if action.help:
            complete.append(f"--description {repr(action.help)}")
        if action.choices:
            choices = repr(' '.join(action.choices))
            complete.append(f"--arguments {choices}")
        if not action.nargs in [0,'?','*'] and len(options) > 0:
            complete.append(f"--require-parameter")
        if action.type == pathlib.Path:
            complete.append(f"--force-files")
            files = True
        else:
            complete.append(f"--no-files")
        if action.help == '==SUPPRESS==':
            continue
        template.append(' '.join(complete))
    template = '\n'.join(template)
    return template


def shell_completion(shell, pkg_parser, add_aliases):
    """Generate a shell completion for a corresponding shell"""
    gen_completion = {
        'fish': fish_completion(pkg_parser, add_aliases),
    }
    return gen_completion[shell]


def get_pkg_module_and_parser(module_and_parser):
    """Import and get package info. Return package module and parser"""
    module, parser = module_and_parser.split(':')
    pkg_module = importlib.import_module(module)
    pkg_parser = getattr(pkg_module, parser)()
    return pkg_module, pkg_parser


def main():
    """Main entry point for the program"""
    parser = parse_arguments()
    args = parser.parse_args()
    pkg_module, pkg_parser = get_pkg_module_and_parser(args.parser)
    add_aliases = args.alias
    for shell in args.shells:
        completion = shell_completion(shell, pkg_parser, add_aliases)
        if (output := args.output):
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(completion)
        else:
            print(completion)


if __name__ == '__main__':
    main()

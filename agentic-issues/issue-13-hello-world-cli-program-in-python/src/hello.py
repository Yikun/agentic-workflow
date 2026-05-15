#!/usr/bin/env python3
"""Hello World CLI Program - A simple command-line greeting tool."""

import argparse
import sys


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hello",
        description="A command-line program that outputs a greeting message.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python hello.py                    Output: Hello, World!
  python hello.py --name Alice       Output: Hello, Alice!
  python hello.py --name "Bob"       Output: Hello, Bob!
""",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="World",
        metavar="<value>",
        help="Custom name for the greeting (default: World)",
    )
    return parser


def generate_greeting(name: str) -> str:
    return f"Hello, {name}!"


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()
    greeting = generate_greeting(args.name)
    print(greeting)
    return 0


if __name__ == "__main__":
    sys.exit(main())

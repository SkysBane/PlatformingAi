"""Compatibility entry point for human play."""

import sys

from cli import main


if __name__ == "__main__":
    raise SystemExit(main(["play", *sys.argv[1:]]))

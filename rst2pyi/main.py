# Copyright 2019 John Reese
# Licensed under the MIT license

import click
from pathlib import Path
from .core import Converter


@click.command(help="convert reStructuredText annotations to python type stubs")
@click.argument(
    "source_dir", type=click.Path(exists=True, file_okay=False, resolve_path=True)
)
@click.argument(
    "dest_dir",
    type=click.Path(exists=False, file_okay=False, writable=True, resolve_path=True),
)
def main(source_dir, dest_dir):
    source_dir = Path(source_dir)
    dest_dir = Path(dest_dir)
    Converter(source_dir, dest_dir).gen_stubs()


if __name__ == "__main__":
    main()

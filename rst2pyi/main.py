# Copyright 2019 John Reese
# Licensed under the MIT license

from pathlib import Path

import click

from .core import Converter


@click.command(help="convert reStructuredText annotations to python type stubs")
@click.argument(
    "source_dir", type=click.Path(exists=True, file_okay=False, resolve_path=True)
)
@click.argument(
    "dest_dir",
    type=click.Path(exists=False, file_okay=False, writable=True, resolve_path=True),
)
def main(source_dir: str = ".", dest_dir: str = "."):
    source = Path(source_dir)
    dest = Path(dest_dir)
    Converter(source, dest).gen_stubs()


if __name__ == "__main__":
    main()

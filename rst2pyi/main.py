# Copyright 2019 John Reese
# Licensed under the MIT license

from pathlib import Path

import click

from .core import Converter, setup_logger


@click.command(help="convert reStructuredText annotations to python type stubs")
@click.option("--debug", "-D", is_flag=True, default=False, help="enable debug logging")
@click.argument(
    "source_dir", type=click.Path(exists=True, file_okay=False, resolve_path=False)
)
@click.argument(
    "dest_dir",
    type=click.Path(exists=False, file_okay=False, writable=True, resolve_path=False),
)
def main(debug: bool = False, source_dir: str = ".", dest_dir: str = "."):
    setup_logger(debug)
    source = Path(source_dir)
    dest = Path(dest_dir)
    Converter(source, dest).gen_stubs()


if __name__ == "__main__":
    main()

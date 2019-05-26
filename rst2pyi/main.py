# Copyright 2019 John Reese
# Licensed under the MIT license

import logging
from pathlib import Path

import click

from rst2pyi import __version__

from .core import Converter, setup_logger

log = logging.getLogger(__name__)


@click.command(help="convert reStructuredText annotations to python type stubs")
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-V", prog_name="rst2pyi")
@click.option("--debug", "-D", is_flag=True, default=False, help="enable debug logging")
@click.option(
    "--validate", "-v", is_flag=True, default=False, help="validate generated stubs"
)
@click.argument(
    "source_dir", type=click.Path(exists=True, file_okay=False, resolve_path=False)
)
@click.argument(
    "dest_dir",
    type=click.Path(exists=False, file_okay=False, writable=True, resolve_path=False),
)
def main(
    debug: bool = False,
    validate: bool = False,
    source_dir: str = ".",
    dest_dir: str = ".",
):
    setup_logger(debug)
    source = Path(source_dir)
    dest = Path(dest_dir)
    stubs = Converter(source, dest).gen_stubs()

    if validate:
        success = True
        from typed_ast.ast3 import parse

        for stub in stubs:
            with open(stub, "r") as f:
                content = f.read()
            try:
                parse(content)
            except Exception:  # pylint: disable=broad-except
                success = False
                log.exception("validation error for %s", stub)

        if not success:
            raise click.ClickException("stub validation failed")


if __name__ == "__main__":
    main()

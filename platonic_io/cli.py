"""Console script for platonic-io."""
import sys
from pathlib import Path

import click

from platonic_io.ocr import LicencePlateOCRReader


@click.group()
def main(args=None):
    """Console script for platonic-io."""
    return 0


@main.command()
@click.argument("image_path")
def ocr(image_path):
    click.echo(LicencePlateOCRReader(image_path=Path(image_path)).read_text())


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

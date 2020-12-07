"""Console script for platonic-io."""
import sys
from pathlib import Path

import click

from platonic_io.GUI import GUI
from platonic_io.ocr import LicencePlateOCRReader
from platonic_io.recognition_engine import Master


@click.group()
def main(args=None):
    """Console script for platonic-io."""
    return 0


@main.command()
@click.argument("image_path")
def ocr(image_path):
    click.echo(LicencePlateOCRReader(image_path=Path(image_path)).read_text())


@main.command(name="process-video")
@click.argument("input_video", type=str)
@click.argument("output_path", type=str)
@click.option("-t", "--threads", default=1, type=int)
def process_video(input_video, output_path, threads=1):
    input_video = Path(input_video)
    output_path = Path(output_path)
    assert input_video.is_file(), "Input file does not exist or is not a file"
    if output_path.is_dir():
        click.secho("Provided output file is a directory", fg="red")
    elif output_path.is_file():
        overwrite = click.prompt(
            "Output file already exist. Do you want to overwrite?(y/n)", type=bool
        )
        if overwrite:
            Path(output_path).unlink()
    Master(str(input_video), str(output_path), threads).start()


@main.command()
@click.option("-t", "--threads", default=1, type=int)
def gui(threads):
    GUI(threads).run()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

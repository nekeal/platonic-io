Platonic-io cli interface
=========================

## Introduction
Platonic-io provides cli interface for easy interacting with core modules.
Below you will find commands with short description.

## Available commands
Basic syntax is `platonic-io [OPTIONS] COMMAND [ARGS]...`

Commands:

1. `gui` - is used to run gui. You can also specify number of threads for video processing
```
Usage: platonic-io gui [OPTIONS]

Options:
  -t, --threads INTEGER
  --help                 Show this message and exit.
```
2. `ocr` - this is interface for `LicencePlateOCRReader` class.
```
Usage: platonic-io ocr [OPTIONS] IMAGE_PATH

Options:
  --help  Show this message and exit.
```
3. `process-video` - this is simple interface for running `Master` class which processes videos.
```
Usage: platonic-io process-video [OPTIONS] INPUT_VIDEO OUTPUT_PATH

Options:
  -t, --threads INTEGER
  --help                 Show this message and exit.
```

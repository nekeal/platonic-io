"""Top-level package for platonic-io."""

__version__ = "0.4.1"

import logging
import sys

logger = logging.getLogger("platonic_io")

_formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger.setLevel(logging.DEBUG)

_sh = logging.StreamHandler(stream=sys.stdout)
_sh.setLevel(logging.DEBUG)
_sh.setFormatter(_formatter)

_fh = logging.FileHandler("platonic-main.log")
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(_formatter)

logger.addHandler(_sh)
logger.addHandler(_fh)

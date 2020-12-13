"""Top-level package for platonic-io."""

__version__ = "0.2.1"

import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
_sh = logging.StreamHandler(stream=sys.stdout)
_sh.setLevel(logging.DEBUG)

_fh = logging.FileHandler("platonic-main.log")
_fh.setLevel(logging.DEBUG)

logger.addHandler(_sh)
logger.addHandler(_fh)

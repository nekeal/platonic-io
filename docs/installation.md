Installation
---

Prerequisites:
==============

Before the installation make sure that following modules were installed:

* Python3 <br>
``` sudo apt-get install python3 ```
* libhdf5-dev <br>
``` sudo apt-get install libhdf5-dev ```
* tesseract-ocr <br>
``` sudo apt-get install tesseract-ocr ```

If you compiled your python from source make sure that you had
`tk-dev` package installed. Otherwise you need to install it and reinstall
your python.

Stable release
==============

To install platonic-io, run this command in your terminal:

    $ poetry add platonic-io

Or in case you don't have poetry just run:

    $ pip install platonic-io


This is the preferred method to install platonic-io, as it will always
install the most recent stable release.

If you don't have [pip](https://pip.pypa.io) installed, this [Python
installation
guide](http://docs.python-guide.org/en/latest/starting/installation/)
can guide you through the process.

From sources
============

The sources for platonic-io can be downloaded from the [Github
repo](https://github.com/nekeal/platonic-io).

You can either clone the public repository:


    $ git clone git://github.com/nekeal/platonic-io

Once you have a copy of the source, you can install it with:

    $ poetry install --no-dev

If you don't have poetry installed:

    $ pip install .

Running project
===============

To run the project, run those commands in your terminal:

    $ platonic-io gui

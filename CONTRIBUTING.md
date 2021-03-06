Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

### Report Bugs

Report bugs at <https://github.com/nekeal/platonic-io/issues>.

If you are reporting a bug, please include:

-   Your operating system name and version.
-   Any details about your local setup that might be helpful in
    troubleshooting.
-   Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and
"help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with
"enhancement" and "help wanted" is open to whoever wants to implement
it.

### Write Documentation

Platonic-io could always use more documentation, whether as part of the
official platonic-io docs, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at
<https://github.com/nekeal/platonic-io/issues>.

If you are proposing a feature:

-   Explain in detail how it would work.
-   Keep the scope as narrow as possible, to make it easier to
    implement.
-   Remember that this is a volunteer-driven project, and that
    contributions are welcome :)

Tools
-----
We use various tools for development to ensure quality of code and to make it
more readable.

* [Flake8](https://github.com/PyCQA/flake8) - Linter for python code
* [Black](https://github.com/psf/black) - Code auto formatter
* [Mypy](https://github.com/python/mypy) - Static type checker
* [Isort](https://github.com/PyCQA/isort) - Tool for sorting imports
* [pre-commmit](https://github.com/pre-commit/pre-commit) - Framework for managing git hooks

Get Started!
------------

!!! note
    We use Poetry for development and we highly recommend you to install
    it globally using official [instruction](https://python-poetry.org/docs/#installation)

Ready to contribute? Here's how to set up platonic-io for local
development.

1.  Fork the platonic-io repo on GitHub.
2.  Clone your fork locally:

        $ git clone git@github.com:<your_username>/platonic-io.git

3. Install project for development

    - Using poetry

            $ cd platonic-io/
            $ poetry install -E test

        Above command will create virtualenv for you and install all necessary packages

    - Using pip and virtualenvwrapper

        Install your local copy into a virtualenv. Assuming you have
        virtualenvwrapper installed, this is how you set up your fork for
        local development:

            $ mkvirtualenv platonic-io
            $ cd platonic-io/
            $ pip install poetry
            $ poetry install -E test

        After that run:

            $ poetry run pre-commit install --install-hooks -t pre-commit -t commit-msg

        Above will configure git hooks which will run before each commit to ensure
        that code is consistent.


4.  Create a branch for local development:

        $ git checkout -b name-of-your-bugfix-or-feature

    Now you can make your changes locally.

5.  When you're done making changes, check that your changes at least pass flake8
    and the tests, including testing other Python versions with tox:

        $ poetry run flake8 platonic-io tests
        $ poetry run pytest
        $ poetry run tox

6.  Commit your changes and push your branch to GitHub:

        $ git add .
        $ git commit -m "Your detailed description of your changes."
        $ git push origin name-of-your-bugfix-or-feature

7.  Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1.  The pull request should include tests.
2.  If the pull request adds functionality, the docs should be updated.
    Put your new functionality into a function with a docstring, and add
    the feature to the list in README.md.
3.  The pull request should work for Python 3.6, 3.7, 3.8 and 3.9. Check
    [Github actions](https://github.com/nekeal/platonic-io/actions?query=event%3Apull_request++) and make sure
    that the tests pass for all supported Python versions.

Tips
----

To run a subset of tests:

    $ poetry run pytest tests

To run an application, remember to enter project venv by typing in project directory:

    $ poetry shell

Deploying
---------

A reminder for the maintainers on how to deploy. Make sure all your
changes are committed (including an entry in CHANGELOG.md). Then run:

    $ poetry version [patch|patch|minor|major|prepatch|preminor|premajor|prerelease]
Then change version in `platonic_io/__init__.py` file and tag your latest commit with appropriate version prefixing it with "v"
for example:

    $ git tag v1.0.0

The push tags to remote:

    $ git push --tags

Github actions will then deploy to PyPI if tests pass.

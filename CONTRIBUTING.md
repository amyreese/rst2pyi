# Contributing to rst2pyi

## Preparation

You'll need to have Python 3.6 available for testing
(I recommend using [pyenv][] for this).

You can do this with pyenv:

    $ pyenv install 3.6.5
    $ pyenv shell 3.6.5


## Setup

Once in your development environment, install the
appropriate linting tools and dependencies:

    $ cd <path/to/rst2pyi>
    $ make dev


## Submitting

Before submitting a pull request, please ensure
that you have done the following:

* Documented changes or features in README.md
* Added appropriate license headers to new files
* Written or modified tests for new functionality
* Used `make format` to format code appropriately
* Validated code with `make lint test`

[pyenv]: https://github.com/pyenv/pyenv

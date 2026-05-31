# print this help message
help:
	just -l

# create venv and install package in editable mode
venv: _tox
	tox devenv

# run all checks and tests
all: pre-commit test coverage

# run pre-commit
pre-commit: _tox
	tox run -e pre-commit

# run tests against all supported python versions
test: _tox
	tox run

# run tests and measure code coverage
coverage: _tox
	tox run -e coverage

# regenerate expected output files for tests
regenerate: _tox
	tox run -e regenerate

_tox:
	uv tool install tox --with tox-uv


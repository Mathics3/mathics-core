# A GNU Makefile to run various tasks - compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

GIT2CL ?= admin-tools/git2cl
PYTHON ?= python3
PIP ?= pip3
BASH ?= bash
RM  ?= rm
PYTEST_OPTIONS ?=
DOCTEST_OPTIONS ?=

# Variable indicating Mathics3 Modules you have available on your system, in latex2doc option format
MATHICS3_MODULE_OPTION ?= --load-module pymathics.graph,pymathics.natlang

.PHONY: \
   all \
   benchmarks \
   build \
   check \
   check-builtin-manifest \
   check-consistency-and-style \
   check-full \
   clean \
   clean-cache \
   clean-cython \
   develop \
   develop-full \
   develop-full-cython \
   dist \
   doc \
   doctest \
   doctest-data \
   djangotest \
   gstest \
   latexdoc \
   mypy \
   plot-detailed-tests\
   pytest \
   pytest-x \
   rmChangeLog \
   test \
   texdoc

MATHICS3_SANDBOX	?=
ifeq ($(OS),Windows_NT)
	MATHICS3_SANDBOX = t
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Darwin)
		MATHICS3_SANDBOX = t
	endif
endif

#: Default target - same as "develop"
all: develop

# run pytest benchmarks
benchmarks:
	BENCHMARKS=True $(PYTHON) -m pytest $(PYTEST_OPTIONS) test/timings

#: build everything needed to install
build:
	$(PYTHON) ./setup.py build

# Note that we need ./setup.py develop
# because pip install doesn't handle
# INSTALL_REQUIRES properly
#: Set up to run from the source tree
develop:  mathics/data/op-tables.json mathics/data/operator-tables.json
	$(PIP) install -e .[dev]

# See note above on ./setup.py
#: Set up to run from the source tree with full dependencies
develop-full:  mathics/data/op-tables.json mathics/data/operators.json
	$(PIP) install -e .[dev,full]

# See note above on ./setup.py
#: Set up to run from the source tree with full dependencies and Cython
develop-full-cython: mathics/data/op-tables.json mathics/data/operators.json
	$(PIP) install -e .[dev,full,cython]


#: Make distribution: wheels, eggs, tarball
dist:
	./admin-tools/make-dist.sh

#: Install Mathics
install:
	$(PYTHON) setup.py install

#: Run the most extensive set of tests
check: pytest gstest doctest

#: Run the most extensive set of tests, stopping on first error
check-x: pytest-x gstest doctest-x plot-detailed-tests

#: Run the most extensive set of tests
check-for-Windows: pytest-for-windows gstest doctest

#: Build and check manifest of Builtins
check-builtin-manifest:
	$(PYTHON) admin-tools/build_and_check_manifest.py

#: Run pytest consistency and style checks
check-consistency-and-style:
	MATHICS_LINT=t $(PYTHON) -m pytest $(PYTEST_OPTIONS) test/consistency-and-style

check-full: check-builtin-manifest check-builtin-manifest check plot-detailed-tests

#: Remove Cython-derived files
clean-cython:
	find mathics -name "*.so" -type f -delete; \
	find mathics -name "*.c" -type f -delete

#: Remove Python cache files
clean-cache:
	find mathics -name *.py[co] -type f -delete; \
	find mathics -name __pycache__ -type d -delete || true

#: Remove derived files
clean: clean-cython clean-cache
	for dir in mathics/doc ; do \
	   ($(MAKE) -C "$$dir" clean); \
	done; \
	rm -f factorials || true; \
	rm -f mathics/data/op-tables || true; \
	rm -rf build || true

mypy:
	mypy --install-types --ignore-missing-imports --non-interactive mathics

plot-detailed-tests:
	MATHICS_CHARACTER_ENCODING="ASCII" MATHICS_PLOT_DETAILED_TESTS="1" $(PYTHON) -m pytest -x $(PYTEST_OPTIONS) test/builtin/drawing/test_plot_detail.py

#: Run pytest tests. Use environment variable "PYTEST_OPTIONS" for pytest options
pytest:
	MATHICS_CHARACTER_ENCODING="ASCII" $(PYTHON) -m pytest $(PYTEST_OPTIONS) $(PYTEST_WORKERS) test

#: Run pytest tests stopping at first failure.
pytest-x :
	PYTEST_OPTIONS="-x" $(MAKE) pytest

#: Run a more extensive pattern-matching test
gstest:
	(cd examples/symbolic_logic/gries_schneider && $(PYTHON) test_gs.py)


#: Create doctest test data and test results that is used to build LaTeX PDF
# For LaTeX docs we assume Unicode
doctest-data: mathics/builtin/*.py mathics/doc/documentation/*.mdoc mathics/doc/documentation/images/*
	MATHICS_CHARACTER_ENCODING="UTF-8" $(PYTHON) mathics/docpipeline.py --output --keep-going $(MATHICS3_MODULE_OPTION)

#: Run tests that appear in docstring in the code. Use environment variable "DOCTEST_OPTIONS" for doctest options
doctest:
	MATHICS_CHARACTER_ENCODING="ASCII" MATHICS3_SANDBOX=$(MATHICS3_SANDBOX) $(PYTHON) mathics/docpipeline.py $(DOCTEST_OPTIONS)

#: Run tests that appear in docstring in the code, stopping on the first error.
doctest-x:
	DOCTEST_OPTIONS="-x" $(MAKE) doctest

#: Make Mathics PDF manual via Asymptote and LaTeX
latexdoc texdoc doc:
	(cd mathics/doc/latex && $(MAKE) doc)

#: Build JSON ASCII to unicode opcode table and operator table
mathics/data/operator-tables.json mathics/data/op-tables.json mathics/data/operators.json:
	$(BASH) ./admin-tools/make-JSON-tables.sh

#: Remove ChangeLog
rmChangeLog:
	$(RM) ChangeLog || true

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@
	patch ChangeLog < ChangeLog-spell-corrected.diff

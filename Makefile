# A GNU Makefile to run various tasks - compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

GIT2CL ?= admin-tools/git2cl
PYTHON ?= python3
PIP ?= pip3
BASH ?= bash
RM  ?= rm

# Variable indicating Mathics3 Modules you have available on your system, in latex2doc option format
MATHICS3_MODULE_OPTION ?= --load-module pymathics.graph,pymathics.natlang

.PHONY: \
   all \
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
   pytest \
   rmChangeLog \
   test \
   texdoc

SANDBOX	?=
ifeq ($(OS),Windows_NT)
	SANDBOX = t
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Darwin)
		SANDBOX = t
	endif
endif

#: Default target - same as "develop"
all: develop

#: build everything needed to install
build:
	$(PYTHON) ./setup.py build

# Note that we need ./setup.py develop
# because pip install doesn't handle
# INSTALL_REQUIRES properly
#: Set up to run from the source tree
develop:  mathics/data/op-tables.json
	$(PIP) install -e .[dev]

# See note above on ./setup.py
#: Set up to run from the source tree with full dependencies
develop-full:  mathics/data/op-tables.json
	$(PIP) install -e .[dev,full]

# See note above on ./setup.py
#: Set up to run from the source tree with full dependencies and Cython
develop-full-cython: mathics/data/op-tables.json
	$(PIP) install -e .[dev,full,cython]


#: Make distirbution: wheels, eggs, tarball
dist:
	./admin-tools/make-dist.sh

#: Install Mathics
install:
	$(PYTHON) setup.py install

#: Run the most extensive set of tests
check: pytest gstest doctest

#: Build and check manifest of Builtins
check-builtin-manifest:
	$(PYTHON) admin-tools/build_and_check_manifest.py

#: Run pytest consistency and style checks
check-consistency-and-style:
	MATHICS_LINT=t $(PYTHON) -m pytest test/consistency-and-style

check-full: check-builtin-manifest check-builtin-manifest check

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

#: Run py.test tests. Use environment variable "o" for pytest options
pytest:
	MATHICS_CHARACTER_ENCODING="ASCII" $(PYTHON) -m pytest $(PYTEST_WORKERS) test $o


#: Run a more extensive pattern-matching test
gstest:
	(cd examples/symbolic_logic/gries_schneider && $(PYTHON) test_gs.py)


#: Create doctest test data and test results that is used to build LaTeX PDF
# For LaTeX docs we assume Unicode
doctest-data: mathics/builtin/*.py mathics/doc/documentation/*.mdoc mathics/doc/documentation/images/*
	MATHICS_CHARACTER_ENCODING="UTF-8" $(PYTHON) mathics/docpipeline.py --output --keep-going $(MATHICS3_MODULE_OPTION)

#: Run tests that appear in docstring in the code.
doctest:
	MATHICS_CHARACTER_ENCODING="ASCII" SANDBOX=$(SANDBOX) $(PYTHON) mathics/docpipeline.py $o

#: Make Mathics PDF manual via Asymptote and LaTeX
latexdoc texdoc doc:
	(cd mathics/doc/latex && $(MAKE) doc)

#: Build JSON ASCII to unicode opcode tables
mathics/data/op-tables.json:
	$(BASH) ./admin-tools/make-op-tables.sh

#: Remove ChangeLog
rmChangeLog:
	$(RM) ChangeLog || true

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@

.PHONY: all clean doc doc-data latex pdf texdoc

PYTHON ?= python
XETEX ?= xelatex
LATEXMK ?= latexmk
BASH ?= /bin/bash
#-quiet

# Location of Python Pickle file containing doctest tests and test results formatted for LaTeX
DOCTEST_LATEX_DATA_PCL ?= $(HOME)/.local/var/Mathics3/doctest_latex_data.pcl

# Variable indicating Mathics3 Modules you have available on your system, in latex2doc option format
MATHICS3_MODULE_OPTION ?=--load-module pymathics.trepan,pymathics.graph,pymathics.natlang

#: Default target: Make everything
all doc texdoc: mathics.pdf

#: Create internal Document Data from .mdoc and Python builtin module docstrings
doc-data $(DOCTEST_LATEX_DATA_PCL):
	(cd ../.. && MATHICS_CHARACTER_ENCODING="UTF-8" $(PYTHON) docpipeline.py --output --keep-going $(MATHICS3_MODULE_OPTION))

mathics-title.pdf:
	cp mathics-title.pdf-src mathics-title.pdf

#: Build somewhat incomplete mathics DVI
mathics.dvi: mathics.tex documentation.tex
	$(LATEXMK) -dvi -f --verbose mathics

mathics.pdf: mathics.tex documentation.tex mathics-title.pdf logo-text-nodrop.pdf logo-heptatom.pdf version-info.tex $(DOCTEST_LATEX_DATA_PCL)
	$(LATEXMK) --verbose -f -pdf -pdflatex="$(XETEX) -halt-on-error" mathics

#: File containing version information
version-info.tex: doc2latex.py
	$(PYTHON) doc2latex.py $(MATHICS3_MODULE_OPTION) && $(BASH) ./sed-hack.sh

#: Build test PDF
mathics-test.pdf: mathics-test.tex testing.tex
	$(LATEXMK) --verbose -f -pdf -pdflatex="$(XETEX) -halt-on-error" mathics-test


#: Generate logos used in the titlepage
logo-heptatom.pdf logo-text-nodrop.pdf:
	(cd .. && $(BASH) ./images.sh)

#: The build of the documentation which is derived from docstrings in the Python code and doctest data
documentation.tex: $(DOCTEST_LATEX_DATA_PCL) ../documentation/1-Manual.mdoc
	$(PYTHON) ./doc2latex.py $(MATHICS3_MODULE_OPTION) && $(BASH) ./sed-hack.sh

#: Same as mathics.pdf
pdf latex: mathics.pdf

#: Remove all auto-generated files
clean:
	rm -f mathics.asy mathics.aux mathics.idx mathics.log mathics.mtc mathics.mtc* mathics.out mathics.toc || true
	rm -f test-mathics.aux test-mathics.idx test-mathics.log test-mathics.mtc test-mathics.mtc* test-mathics.out test-mathics.toc || true
	rm -f mathics.fdb_latexmk mathics.ilg mathics.ind mathics.maf mathics.pre || true
	rm -f mathics-*.??? || true
	rm -f mathics-test.asy mathics-test.aux mathics-test.idx mathics-test.log mathics-test.mtc mathicsest.mtc* mathics-test.out mathics-test.toc || true
	rm -f documentation.tex $(DOCTEST_LATEX_DATA_PCL) || true
	rm -f mathics.pdf mathics.dvi test-mathics.pdf test-mathics.dvi || true
	rm -f mathics-test.pdf mathics-test.dvi version-info.tex || true

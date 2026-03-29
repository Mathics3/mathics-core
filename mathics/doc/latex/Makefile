.PHONY: all clean doc doc-data latex pdf texdoc mathics-xetex.pdf mathics-asy-pdf

PYTHON ?= python
XETEX ?= xelatex
LATEXMK ?= latexmk
BASH ?= /bin/bash
#-quiet

# Get all matching .asy files using shell globbing
ASY_FILES := $(shell ls mathics3-[0-9].asy mathics3-[0-9][0-9].asy mathics3-[0-9][0-9][0-9].asy 2>/dev/null)

# Derive the PDF filenames from the .asy filenames
ASY_PDF_FILES := $(ASY_FILES:.asy=.pdf)

# Pattern rule to convert and asymptote .asy file to a to .pdf figure.
# This matches any .pdf file and looks for a corresponding .asy file
%.pdf: %.asy
	asy -f pdf $<

# Location of Python Pickle file containing doctest tests and test results formatted for LaTeX
DOCTEST_LATEX_DATA_PCL ?= $(HOME)/.local/var/Mathics3/doctest_latex_data.pcl

# Variable indicating Mathics3 Modules you have available on your system, in latex2doc option format
MATHICS3_MODULE_OPTION ?=--load-module pymathics.graph,pymathics.natlang

#: Default target: Make everything
all doc texdoc: mathics3.pdf

#: Create internal Document Data from .mdoc and Python builtin module docstrings
doc-data $(DOCTEST_LATEX_DATA_PCL):
	(cd ../.. && MATHICS_CHARACTER_ENCODING="UTF-8" $(PYTHON) docpipeline.py --output --keep-going $(MATHICS3_MODULE_OPTION))

mathics3-title.pdf:
	cp mathics3-title.pdf-src mathics3-title.pdf

#: Build somewhat incomplete mathics DVI
mathics3.dvi: mathics3.tex documentation.tex
	$(LATEXMK) -dvi -f --verbose mathics3

#: Build main Mathcis3 PDF
mathics3.pdf: mathics3.tex documentation.tex mathics3-title.pdf logo-text-nodrop.pdf logo-heptatom.pdf version-info.tex $(DOCTEST_LATEX_DATA_PCL) $(ASY_FILES)
	$(LATEXMK) --verbose -f -pdf -pdflatex="$(XETEX) -halt-on-error" mathics3

#: Rebuild all Aymptote PDF figures from .asy files
mathics3-asy-pdf: $(ASY_PDF_FILES)

#: Use this if latexmk des not work. It runx
mathics3-xetex.pdf: mathics3.tex documentation.tex mathics3-title.pdf logo-text-nodrop.pdf logo-heptatom.pdf version-info.tex $(DOCTEST_LATEX_DATA_PCL)
	xelatex -halt-on-error -recorder "mathics3.tex"

#: File containing version information
version-info.tex: doc2latex.py
	$(PYTHON) doc2latex.py $(MATHICS3_MODULE_OPTION) && $(BASH) ./sed-hack.sh

#: Build test PDF
mathics3-test.pdf: mathics-test.tex testing.tex
	$(LATEXMK) --verbose -f -pdf -pdflatex="$(XETEX) -halt-on-error" mathics3-test

#: Build main Mathcis3 PDF
mathics3-???.pdf: mathics.tex documentation.tex mathics3-title.pdf logo-text-nodrop.pdf logo-heptatom.pdf version-info.tex $(DOCTEST_LATEX_DATA_PCL)
	$(LATEXMK) --verbose -f -pdf -pdflatex="$(XETEX) -halt-on-error" mathics


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
	rm -f mathics3.asy mathics3.aux mathics3.idx mathics3.log mathics3.mtc mathics3.mtc* mathics3.out mathics3.toc || true
	rm -f test-mathics3.aux test-mathics3.idx test-mathics3.log test-mathics3.mtc test-mathics3.mtc* test-mathics3.out test-mathics3.toc || true
	rm -f mathics3.fdb_latexmk mathics3.ilg mathics3.ind mathics3.maf mathics3.pre || true
	rm -f $(ASY_FILES) $(ASY_PDF_FILES) || true
	rm -f mathics3-test.asy mathics3-test.aux mathics3-test.idx mathics3-test.log mathics3-test.mtc mathics3est.mtc* mathics3-test.out mathics3-test.toc || true
	rm -f documentation.tex $(DOCTEST_LATEX_DATA_PCL) || true
	rm -f mathics3.pdf mathics3.dvi test-mathics3.pdf test-mathics3.dvi || true
	rm -f mathics3-test.pdf mathics3-test.dvi version-info.tex || true

#!/bin/bash
# The program create PDF images that can be embedded into the
# Mathics manual. In particular the Mathics heptatom logo and the
# Mathics logo with a shadow that extends a little bit down forward right.


bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
cd $mydir
mydir=$(pwd)
DOC_DIR=$(pwd)

if [[ -n $DOCTEST_LATEX_DATA_PCL ]]; then
    LATEX_DIR=$(basename $DOCTEST_LATEX_DATA_PCL)
else
    LATEX_DIR=${mydir}/latex
fi
LATEX_IMAGE_DIR=${LATEX_DIR}/images
DOC_IMAGE_DIR=${DOC_DIR}/documentation/images

if [[ ! -d "$DOC_IMAGE_DIR" ]] ; then
    mkdir -p $DOC_IMAGE_DIR
fi

for filename in $(find documentation/images/ -name "*.eps"); do
	pdf="${DOC_IMAGE_DIR}/$(basename "$filename" .eps).pdf"
	epstopdf "$filename"
	mv "$pdf" $LATEX_IMAGE_DIR
done

for filename in ${mydir}/images/logo-{heptatom,heptatom-Mathics3,Mathics3-nodrop}.svg; do
    inkscape $filename --export-filename="latex/images/$(basename "$filename" .svg).pdf" --batch-process
done

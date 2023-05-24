#!/bin/bash
# The program create PDF images that can be imbedded into the
# Mathics manual. In particular the Mathics heptatom logo and the
# Mathics logo with a shadow that extends a little bit down forward right.


bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
cd $mydir
mydir=$(pwd)

if [[ -n $DOCTEST_LATEX_DATA_PCL ]]; then
    LATEX_DIR=$(basename $DOCTEST_LATEX_DATA_PCL)
else
    LATEX_DIR=${mydir}/latex
fi
IMAGE_DIR=${LATEX_DIR}/images

if [[ ! -d "$IMAGE_DIR" ]] ; then
    mkdir -p $IMAGE_DIR
fi

for filename in $(find documentation/images/ -name "*.eps"); do
	pdf="${LATEX_DIR}/$(basename "$filename" .eps).pdf"
	epstopdf "$filename"
	mv "$pdf" $IMAGE_DIR
done

for filename in ${mydir}/images/logo-{heptatom,text-nodrop}.svg; do
    inkscape $filename --export-filename="latex/$(basename "$filename" .svg).pdf" --batch-process
done

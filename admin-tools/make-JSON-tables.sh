#!/bin/bash
# Create ASCII operator to Unicode tables
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
PYTHON=${PYTHON:-python}

cd $mydir/../mathics/data
mathics3-make-boxing-character-json -o boxing-characters.json

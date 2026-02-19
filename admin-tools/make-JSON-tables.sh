#!/bin/bash
# Create ASCII operator to Unicode tables
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
PYTHON=${PYTHON:-python}

cd $mydir/../mathics/data
mathics3-make-boxing-character-json -o boxing-characters.json
mathics3-make-named-character-json -o named-characters.json
mathics3-make-operator-json -o operators.json

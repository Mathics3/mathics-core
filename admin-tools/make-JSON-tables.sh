#!/bin/bash
# Create ASCII operator to Unicode tables
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
PYTHON=${PYTHON:-python}

cd $mydir/../mathics/data
mathics3-generate-json-table -o character-tables.json
mathics3-generate-operator-json-table -o operator-tables.json
# tokenizer looks for the table in the default place...
mathics3-generate-operator-json-table

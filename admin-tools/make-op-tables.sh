#!/bin/bash
# Create ASCII operator to Unicode tables
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
PYTHON=${PYTHON:-python}

cd $mydir/../mathics/data
mathics3-generate-json-table \
    --field=ascii-operator-to-symbol \
    --field=ascii-operator-to-unicode \
    --field=ascii-operator-to-wl-unicode \
    --field=operator-to-ascii \
    --field=operator-to-unicode \
    -o op-tables.json
mathics3-generate-operator-json-table -o operator-tables.json
# tokenizer looks for the table in the default place...
mathics3-generate-operator-json-table

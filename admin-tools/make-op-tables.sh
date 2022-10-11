#!/bin/bash
# Create ASCII operator to Unicode tables
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
PYTHON=${PYTHON:-python}

cd $mydir/../mathics/data
mathics-generate-json-table \
    --field=ascii-operator-to-symbol \
    --field=ascii-operator-to-unicode \
    --field=ascii-operator-to-wl-unicode \
    --field=operator-to-ascii \
    --field=operator-to-unicode \
    -o op-tables.json

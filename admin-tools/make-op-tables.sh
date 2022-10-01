#!/bin/bash
# Create ASCII operator to Unicode tables
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
PYTHON=${PYTHON:-python}

cd $mydir/../mathics/data
mathics-generate-json-table --field=ascii-operator-to-unicode --field=ascii-operator-to-wl-unicode -o op-tables.json

#!/bin/bash
PACKAGE=mathics3

# FIXME put some of the below in a common routine
function finish {
  cd $mathics_core_owd
}

cd $(dirname ${BASH_SOURCE[0]})
mathics_core_owd=$(pwd)
trap finish EXIT

if ! source ./pyenv-versions ; then
    exit $?
fi

cd ..
source mathics/version.py
cp -v ${HOME}/.local/var/mathics/doctest_latex_data.pcl mathics/data/

echo $__version__

for pyversion in $PYVERSIONS; do
    if ! pyenv local $pyversion ; then
	exit $?
    fi
    rm -fr build
    # PYPI no longer supports eggs
    # python setup.py bdist_egg
    python setup.py bdist_wheel
done

python ./setup.py sdist
finish

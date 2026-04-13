#!/bin/bash
set -x
# Brute force convert Unicode characters in LaTeX that it can't handle
# Workaround for messages of the form:
#    Missing character: There is no ⩵ ("2A75) in font pplr7t!
# Mathics3 MakeBox rules should handle this but they don't.

# Characters that only work in math mode we convert back
# to their ASCII equivalent. Otherwise, since we don't
# understand context, it might not be right to
# use a math-mode designation.
if [[ -f documentation.tex ]] ; then
    cp documentation.tex{,-before-sed}
fi

sed -i -e 's/Φ/$\\\\Phi$/g' documentation.tex
sed -i -e 's/⩵/==/g' documentation.tex

sed -i -e s/μ/$\\\\mu$/g documentation.tex
sed -i -e s/reference-of-built-in-symbols/r/g documentation.tex
sed -i -e s/integer-and-number-theoretical-functions/int-fns/g documentation.tex
sed -i -e s/mathematical-constants/math-consts/g documentation.tex

# sed -i -e "s:'[\$]Path':\$Path:g" documentation.tex

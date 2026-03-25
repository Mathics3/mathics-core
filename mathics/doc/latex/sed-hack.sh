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

# Greek Symbols
sed -i -e 's/Φ/$\\\\Phi$/g' documentation.tex
sed -i -e s/μ/$\\\\mu$/g documentation.tex

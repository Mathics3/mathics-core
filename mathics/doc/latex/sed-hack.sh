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

sed -i -e 's/ⅅ/$\\mathbb{D}$/' documentation.tex
# Greek
sed -i -e 's/Φ/$\\\\Phi$/g' documentation.tex
sed -i -e s/μ/$\\\\mu$/g documentation.tex


# TODO: find the right LaTeX representation for these characters
sed -i -e 's/ç/\\c{c}/g' documentation.tex
sed -i -e 's/ñ/\\~n/g' documentation.tex
sed -i -e 's/ê/\\^e/g' documentation.tex
sed -i -e "s/é/\\\'e/g" documentation.tex

# other...
# Happends in GreaterEqual, probably because an error
# into the tables
sed -i -e 's/≖/=||=/g' documentation.tex

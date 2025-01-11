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
sed -i -e s/π/\\\\pi/g documentation.tex
sed -i -e s/“/\`\`/g documentation.tex
sed -i -e s/”/''/g documentation.tex
sed -i -e s/”/''/g documentation.tex
sed -i -e s/″/''/g documentation.tex
# sed -i -e s/\\′/'/g documentation.text
#sed -i -e s/′/'/ documentation.tex
sed -i -e 's/–/--/g' documentation.tex

# Greek
sed -i -e 's/Φ/$\\\\Phi$/g' documentation.tex
sed -i -e 's/ϕ/phi/g' documentation.tex
sed -i -e s/μ/$\\\\mu$/g documentation.tex

sed -i -e 's/⧴/:>/g' documentation.tex
sed -i -e 's/—/-/g' documentation.tex
sed -i -e 's/≤/<=/g' documentation.tex
sed -i -e 's/≠/!=/g' documentation.tex
sed -i -e 's/⩵/==/g' documentation.tex
sed -i -e 's/∧/&&/g' documentation.tex
sed -i -e 's/⧦/\\\\Equiv/g' documentation.tex
sed -i -e 's/⊻/xor/g' documentation.tex
sed -i -e 's/∧/&&/g' documentation.tex
sed -i -e 's/‖/||/g' documentation.tex
sed -i -e 's/ⅅ/$\\mathbb{D}$/' documentation.tex
sed -i -e 's/→/->/g' documentation.tex

# This kind of tick mark appears in latitude/longitude "minute" tick marks of ExampleData/PrimeMeridian.html
sed -i -e "s/′/'/g" documentation.tex

# assumes LaTeX gensymb package
sed -i -e "s/°/\\\\degree{}/g" documentation.tex

# Work around a doc2latex.py bug which strips "s"
# from Properties in a Section heading.
# TODO: figure out how to fix that bug.
sed -i -e "s/Propertie\\\\/Properties\\\\/g" documentation.tex

# TODO: find the right LaTeX representation for these characters
sed -i -e 's/ç/\\c{c}/g' documentation.tex
sed -i -e 's/ñ/\\~n/g' documentation.tex
sed -i -e 's/ê/\\^e/g' documentation.tex
sed -i -e 's/≖/=||=/g' documentation.tex
sed -i -e 's/⇒/==>/g' documentation.tex
sed -i -e "s/é/\\\'e/g" documentation.tex

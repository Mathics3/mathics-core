#!/bin/bash
set -x
# Brute force convert Unicode characters in LaTeX that it can't handle
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
sed -i -e s/μ/$\\\\mu$/g documentation.tex
sed -i -e s/–/--/g documentation.tex
sed -i -e s/Φ/$\\\\Phi$/g documentation.tex

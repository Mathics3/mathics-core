#!/bin/bash
# Brute force convert Unicode characters in LaTeX that it can't handle
cp documentation.tex{,-before-sed}
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

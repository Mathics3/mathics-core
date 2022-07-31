#!/bin/bash
# Brute force convert Unicode characters in LaTeX that it can't handle
cp documentation.tex{,-before-sed}
sed -i -e s/π/\\\\pi/ documentation.tex
sed -i -e s/“/\`\`/ documentation.tex
sed -i -e s/”/''/ documentation.tex
sed -i -e s/”/''/ documentation.tex
sed -i -e s/′/\'/ documentation.tex
sed -i -e s/μ/$\\\\mu$/ documentation.tex
sed -i -e s/–/--/ documentation.tex
sed -i -e s/Φ/$\\\\Phi$/ documentation.tex

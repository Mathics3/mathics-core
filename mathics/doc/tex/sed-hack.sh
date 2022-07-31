#!/bin/bash
# Brute force convert Unicode characters in LaTeX that it can't handle
sed -i -e s/π/\\\\pi/ documentation.tex
sed -i -e s/“/\`\`/ documentation.tex
sed -i -e s/”/''/ documentation.tex
sed -i -e s/”/''/ documentation.tex
sed -i -e s/′/\'/ documentation.tex
sed -i -e s/μ/\\\\mu/ documentation.tex
sed -i -e s/–/--/ documentation.tex
sed -i -e s/Φ/\\\\Phi/ documentation.tex

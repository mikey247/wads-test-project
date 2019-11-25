#!/bin/bash

# gen_css.sh
# --------------------------------------------------------------------------------------------------------------------
# Generate CSS files for all of the syntax styles (colour schemes) that Pygmentize supports
# --------------------------------------------------------------------------------------------------------------------
# Run this script in this directory (sitecore/static/sitecore/pygments) to generate CSS files for all available styles
# Gets a list of style names that can be passed to the pgymentize -S option to export CSS
#
# Requires:
#   pygmentize binary installed in the virtualenv
#
# Notes on bash script:
#
# -L styles
#    List styles and their descriptions (names on own lines in format of "* NAME:"
# grep/sed
#    Filter "* NAME:" lines, and strip "* " from start and ":" from end of line
# -f html
#    We're using pygments in HTML in code blocks of Streamfield
# -S NAME
#    An individual style name from the list
# -a .syntax
#    Append the selector "syntax" to the defined CSS

STYLES=$(pygmentize -L styles | grep -e "^* " | sed -e 's/^\* //g' | sed -e 's/:$//g')
SELECTOR=".highlight"

for STYLE in ${STYLES}; do
    pygmentize -f html -S ${STYLE} -a ${SELECTOR} > ${STYLE}.css;
done

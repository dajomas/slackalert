#!/bin/bash

# This script can be used for debugging
# If something goes wrong, let the alert run this script in stead of the python script
# To capture the output of the python script into a file

[[ ! -d $(dirname $0)/../tmp ]] && mkdir -p $(dirname $0)/../tmp

OUTFILE=$(dirname $0)/../tmp/$(basename $0 .sh).out
echo "******************************" >> ${OUTFILE}
echo "* $(date)" >> ${OUTFILE}
echo "******************************" >> ${OUTFILE}
echo "$@" >> ${OUTFILE}
echo "******************************" >> ${OUTFILE}
python $(dirname $0)/action_$(basename $0 .sh).py "$@" >> ${OUTFILE} 2>&1
echo "******************************" >> ${OUTFILE}

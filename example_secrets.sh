#!/bin/bash

# This is a simple file to show how to set a Snyk tokens as ENV Variables

# add snyk token here
export SNYK_TOKEN="BD832F91-A742-49E9-BC1E-411E0C8743EA"

# save this file
# and load it with the command: source example_secrets.sh
# now check that these variables are set running the commands:
# echo $SNYK_TOKEN

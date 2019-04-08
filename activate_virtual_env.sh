#!/bin/bash
# .---------- constant part!
# vvvv vvvv-- the code from above
RED='\033[01;31m'
GREEN='\033[01;32m'
YELLOW='\033[01;33m'
BLUE='\033[01;34m'
PURPLE='\033[01;35m'
CYAN='\033[01;36m'
WHITE='\033[01;37m'
BOLD='\033[1m'
UNDERLINE='\033[4m'
NC='\033[0m' # No Color

FAIL_ICON="${RED}✘${NC}"
PASS_ICON="${GREEN}✔${NC}"

echo "${GREEN}Activating virtual environment for this project.${NC}"
source ./server/env/bin/activate
# TODO if windows, activate the windows virtual env
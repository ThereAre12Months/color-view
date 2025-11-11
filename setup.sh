#!/usr/bin/env bash

# set cwd to local folder
cd "${0%/*}"

if ! command -v python3 >/dev/null; then
	echo "ERROR: python3 not found on $PATH"
	exit 1
fi

# setup venv
if [ ! -d ./.venv/ ]; then
	echo "INFO: creating virtual environment"
	python3 -m venv .venv
fi
source ./.venv/bin/activate

# upgrade all requirements
echo "INFO: installing/upgrading pip and requirements"
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade -r requirements.txt

# exit venv
deactivate

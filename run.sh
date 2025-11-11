#!/usr/bin/env bash

cd "${0%/*}"

source .venv/bin/activate
python3 main.py

deactivate

#!/usr/bin/env bash

set -e
set -x

coverage run --source=src -m pytest -lv ${ARGS}

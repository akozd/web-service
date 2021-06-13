#!/bin/bash

if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    virtualenv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

pushd infrastructure

cdk deploy --require-approval never

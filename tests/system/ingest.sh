#!/bin/sh

cd ../../deploy
ansible-playbook ../tests/system/ingest.yaml


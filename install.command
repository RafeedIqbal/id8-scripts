#!/usr/bin/env bash
cd "$(dirname "$0")/src"
echo "Running id8-scripts installer..."
python3 install_id8_workflow.py
echo "Press any key to exit..."
read -n 1 -s -r -p ""
echo

#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Running id8-scripts installer..."
python3 "$SCRIPT_DIR/src/install_id8_workflow.py"
echo "Press any key to exit..."
read -n 1 -s -r -p ""
echo

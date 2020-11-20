#!/bin/bash

# We need to encode output as base64, because In Bash, you can't store the NULL-character in a variable.
OUTPUT=$(PYTHONPATH=$PROJ_DIR/fox.cub.utils/ $PYTHON $PROJ_DIR/fox.cub.utils/parsers/pinnacle_client.py -u $PIN_USR -p $PIN_PWD | base64)
echo "$OUTPUT" | base64 -d | PYTHONPATH=$PROJ_DIR/fox.cub.utils/ $PYTHON $PROJ_DIR/fox.cub.utils/scripts/process_market_changes.py

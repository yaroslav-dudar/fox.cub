#!/bin/bash

OUTPUT=$(PYTHONPATH=$PROJ_DIR/fox.cub.utils/ $PYTHON $PROJ_DIR/fox.cub.utils/scripts/dummy_shared_data.py | base64)
echo "$OUTPUT" | base64 -d | PYTHONPATH=$PROJ_DIR/fox.cub.utils/ $PYTHON $PROJ_DIR/fox.cub.utils/scripts/process_market_changes.py

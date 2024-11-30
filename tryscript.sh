#!/bin/bash

echo "====TEST FILE INPUT1_CLASSIC_NODES.IN===="
python3 src/acstsp.py data/input1_classic_nodes.in --iterations=5 --n=5
echo ""
echo ""
echo "====TEST FILE INPUT3_HOUSE_NODES.IN===="
python3 src/acstsp.py data/input3_house_nodes.in --display --iterations=5 --n=5
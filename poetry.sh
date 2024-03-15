#!/bin/bash

# Check if poetry environment already exists

poetry env info --path
if [ $? -eq 0 ]; then
    echo "Poetry env already exists"
else
    echo "Poetry env does not exist. Creating..."
    poetry init -n
fi

# Add your additional commands here
echo Welcome to paperq... enable the poetry env with `poetry shell` command.

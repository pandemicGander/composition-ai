#!/bin/bash

# Clear the file first
> prompt.txt

# Append the tree structure excluding certain directories
tree -I .idea -I venv -I midi_bucket >> prompt.txt 2>/dev/null

# Find and process Python files in the `src` folder, excluding __init__.py
find src -type f -name "*.py" ! -name "__init__.py" | while read -r file; do
    echo "### $file ###" >> prompt.txt  # Append the file name
    cat "$file" >> prompt.txt           # Append the file content
    echo -e "\n" >> prompt.txt          # Add a newline for separation
done

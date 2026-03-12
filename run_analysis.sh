#!/bin/bash

# Shell script to run GDB Spatial Analysis on Linux/macOS

echo ""
echo "========================================"
echo "ESRI File Geodatabase Spatial Analysis"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.7+ using:"
    echo "  macOS: brew install python"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python $python_version"

# Check if required packages are installed
echo "Checking required packages..."

python3 -c "import geopandas; import pandas; import fiona; import shapely; import matplotlib" 2>/dev/null

if [ $? -ne 0 ]; then
    echo ""
    echo "Required packages not found. Installing from requirements.txt..."
    echo ""
    pip3 install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "Error installing packages. Please run manually:"
        echo "  pip3 install -r requirements.txt"
        exit 1
    fi
fi

# Run the analysis script
echo ""
echo "Starting analysis..."
echo ""

python3 gdb_spatial_analysis.py

if [ $? -eq 0 ]; then
    echo ""
    echo "Analysis completed successfully!"
    echo "Results saved in: analysis_results/"
    echo ""
else
    echo ""
    echo "Analysis completed with errors. See messages above."
    echo ""
fi

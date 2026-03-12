@echo off
REM Batch script to run GDB Spatial Analysis on Windows

echo.
echo ========================================
echo ESRI File Geodatabase Spatial Analysis
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import geopandas; import pandas; import fiona; import shapely; import matplotlib" >nul 2>&1

if errorlevel 1 (
    echo.
    echo Required packages not found. Installing from requirements.txt...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error installing packages. Please run manually:
        echo   pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM Run the analysis script
echo.
echo Starting analysis...
echo.

python gdb_spatial_analysis.py

if errorlevel 1 (
    echo.
    echo Analysis completed with errors. See messages above.
    pause
) else (
    echo.
    echo Analysis completed successfully!
    echo Results saved in: analysis_results/
    echo.
)

REM Optional: Keep window open
pause

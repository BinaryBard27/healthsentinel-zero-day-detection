@echo off
REM ============================================================================
REM LSTM Autoencoder Training - One-Click Setup
REM ============================================================================
REM 
REM This script trains the LSTM autoencoder for insider threat detection.
REM 
REM Prerequisites:
REM - Python 3.8+
REM - Required packages (will be installed if missing)
REM
REM Author: HealthSentinel Team
REM ============================================================================

echo.
echo ================================================================================
echo LSTM AUTOENCODER TRAINING - HEALTHSENTINEL
echo ================================================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [1/5] Checking Python installation...
python --version
echo.

REM Check required packages
echo [2/5] Checking required packages...
python -c "import torch" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyTorch...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
)

python -c "import pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install pandas numpy scikit-learn matplotlib seaborn
)

echo Required packages installed.
echo.

REM Check data file
echo [3/5] Checking data file...
set DATA_FILE=Datasets\merged_all_logs_complete.csv

if not exist "%DATA_FILE%" (
    echo WARNING: Data file not found at %DATA_FILE%
    echo Please ensure the merged log file exists.
    pause
    exit /b 1
)

for %%A in ("%DATA_FILE%") do set SIZE_MB=%%~zA
set /a SIZE_MB=%SIZE_MB% / 1048576
echo Found: %DATA_FILE% (%SIZE_MB% MB)
echo.

REM Create output directory
echo [4/5] Creating output directory...
if not exist "models\insider_threat_autoencoder" mkdir models\insider_threat_autoencoder
echo Output: models\insider_threat_autoencoder\
echo.

REM Training
echo [5/5] Starting training...
echo.
echo ================================================================================
echo TRAINING IN PROGRESS
echo ================================================================================
echo.
echo Expected time: 15-20 minutes (GPU) or 40-60 minutes (CPU)
echo.
echo Model will be saved to: models\insider_threat_autoencoder\
echo.

python notebooks\train_lstm_autoencoder.py

if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo TRAINING FAILED
    echo ================================================================================
    echo.
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo TRAINING COMPLETE!
echo ================================================================================
echo.
echo Output files:
echo   - models\insider_threat_autoencoder\best_autoencoder.pt
echo   - models\insider_threat_autoencoder\user_baselines.json
echo   - models\insider_threat_autoencoder\training_results.json
echo   - models\insider_threat_autoencoder\training_curve.png
echo   - models\insider_threat_autoencoder\error_distribution.png
echo.
echo Next steps:
echo   1. Review training_curve.png and error_distribution.png
echo   2. Test detection: python src\insider_threat_detector.py
echo   3. Optional: Train hybrid detection with Isolation Forest
echo.
pause

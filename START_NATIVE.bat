@echo off
REM Native Windows Startup Script for EY Banking AI
REM No Docker - Direct execution with GPU/NPU support

echo ================================================
echo   EY Banking AI - Native Windows Startup
echo   GPU: NVIDIA RTX 5070 (CUDA 13.0)
echo   NPU: Intel AI Boost
echo ================================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "backend\gpuenv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Creating new environment...
    python -m venv backend\gpuenv
    echo.
)

REM Activate virtual environment
echo [1/4] Activating Python environment...
call backend\gpuenv\Scripts\activate.bat
echo.

REM Install/Update dependencies with CUDA 13.0
echo [2/4] Installing dependencies (CUDA 13.0)...
pip install --upgrade pip
pip install -r backend\requirements.txt
echo.

REM Clear GPU memory
echo [3/4] Clearing GPU cache...
python -c "import torch; torch.cuda.empty_cache() if torch.cuda.is_available() else None; print('GPU cache cleared')"
echo.

REM Verify GPU/NPU setup
echo [4/4] Verifying hardware acceleration...
python -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}'); print(f'GPU Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}'); print(f'CUDA Version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')"
echo.

REM Start the application
echo ================================================
echo   Starting FastAPI application on port 8000
echo   GPU/NPU acceleration ENABLED
echo ================================================
echo.
echo Access the API at: http://localhost:8000
echo Documentation: http://localhost:8000/docs
echo.

cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause

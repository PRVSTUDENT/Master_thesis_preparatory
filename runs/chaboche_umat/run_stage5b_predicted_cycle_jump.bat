@echo off
REM Stage 5B predicted-state FE cycle-jump continuation.

setlocal enabledelayedexpansion

cd /d D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat

echo ============================================================
echo Loading Intel oneAPI + Visual Studio Build Tools environment
echo ============================================================

set "VS2022INSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64

echo.
echo ============================================================
echo Checking compiler/linker/Abaqus availability
echo ============================================================

where ifx
if errorlevel 1 (
    echo ERROR: ifx not found after setvars.
    pause
    exit /b 1
)

where link
if errorlevel 1 (
    echo ERROR: Microsoft LINK not found after setvars.
    pause
    exit /b 1
)

where abaqus
if errorlevel 1 (
    echo ERROR: Abaqus not found.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Stage 5B datacheck
echo ============================================================

call abaqus job=chaboche_stage5b_predicted_cycle19_to_cycle20_check ^
    input=chaboche_stage5b_predicted_cycle19_to_cycle20.inp ^
    user=umat_chaboche_v1_with_sdvini_sigini_predicted_cycle19.f ^
    datacheck interactive

if errorlevel 1 (
    echo ERROR: Stage 5B datacheck failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Stage 5B full predicted cycle-jump analysis
echo ============================================================

call abaqus job=chaboche_stage5b_predicted_cycle19_to_cycle20 ^
    input=chaboche_stage5b_predicted_cycle19_to_cycle20.inp ^
    user=umat_chaboche_v1_with_sdvini_sigini_predicted_cycle19.f ^
    interactive ask_delete=OFF scratch=.

if errorlevel 1 (
    echo ERROR: Stage 5B full analysis failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Stage 5B predicted cycle-jump analysis completed.
echo ============================================================
pause

@echo off
REM Stage 9B predicted cycle-49 to cycle-50 FE validation.

setlocal enabledelayedexpansion
cd /d %~dp0

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
if errorlevel 1 exit /b 1

where link
if errorlevel 1 exit /b 1

where abaqus
if errorlevel 1 exit /b 1

echo.
echo ============================================================
echo Stage 9B datacheck
echo ============================================================

call abaqus job=chaboche_stage9b_predicted_cycle49_to_cycle50_check ^
    input=chaboche_stage9b_predicted_cycle49_to_cycle50.inp ^
    user=umat_chaboche_v1_with_sdvini_sigini_predicted_cycle49.f ^
    datacheck interactive scratch=.

if errorlevel 1 exit /b 1

echo.
echo ============================================================
echo Stage 9B full predicted cycle-jump analysis
echo ============================================================

call abaqus job=chaboche_stage9b_predicted_cycle49_to_cycle50 ^
    input=chaboche_stage9b_predicted_cycle49_to_cycle50.inp ^
    user=umat_chaboche_v1_with_sdvini_sigini_predicted_cycle49.f ^
    interactive ask_delete=OFF scratch=.

if errorlevel 1 exit /b 1

echo.
echo Stage 9B predicted cycle-jump analysis completed.

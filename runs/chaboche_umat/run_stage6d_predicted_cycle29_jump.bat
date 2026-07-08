@echo off
REM Stage 6D predicted cycle-29 to cycle-30 FE cycle-jump validation.

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
echo Stage 6D datacheck
echo ============================================================

call abaqus job=chaboche_stage6d_predicted_cycle29_to_cycle30_check ^
    input=chaboche_stage6d_predicted_cycle29_to_cycle30.inp ^
    user=umat_chaboche_v1_with_sdvini_sigini_predicted_cycle29.f ^
    datacheck interactive scratch=.

if errorlevel 1 (
    echo ERROR: Stage 6D datacheck failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Stage 6D full predicted cycle-jump analysis
echo ============================================================

call abaqus job=chaboche_stage6d_predicted_cycle29_to_cycle30 ^
    input=chaboche_stage6d_predicted_cycle29_to_cycle30.inp ^
    user=umat_chaboche_v1_with_sdvini_sigini_predicted_cycle29.f ^
    interactive ask_delete=OFF scratch=.

if errorlevel 1 (
    echo ERROR: Stage 6D full analysis failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Stage 6D predicted cycle-jump analysis completed.
echo ============================================================
pause

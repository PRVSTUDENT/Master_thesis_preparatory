@echo off
REM Stage 6A full explicit 50-cycle Chaboche-v1 reference.

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
echo Stage 6A 50-cycle reference datacheck
echo ============================================================

call abaqus job=chaboche_vp_v1_cyclic_eps005_50cycles_check ^
    input=chaboche_vp_v1_cyclic_eps005_50cycles.inp ^
    user=umat\chaboche_vp_v1_working.f ^
    datacheck interactive

if errorlevel 1 (
    echo ERROR: 50-cycle datacheck failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Stage 6A full 50-cycle reference analysis
echo ============================================================

call abaqus job=chaboche_vp_v1_cyclic_eps005_50cycles ^
    input=chaboche_vp_v1_cyclic_eps005_50cycles.inp ^
    user=umat\chaboche_vp_v1_working.f ^
    interactive ask_delete=OFF scratch=.

if errorlevel 1 (
    echo ERROR: 50-cycle full analysis failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Stage 6A 50-cycle reference analysis completed.
echo ============================================================
pause

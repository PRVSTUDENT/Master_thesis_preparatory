@echo off
setlocal

cd /d D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat

echo ============================================================
echo Loading Intel oneAPI + Visual Studio Build Tools environment
echo ============================================================

set "VS2022INSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64

echo.
echo ============================================================
echo Checking compiler/linker availability
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
echo Case A: STATEV-only datacheck
echo ============================================================

call abaqus job=chaboche_stage4b_statev_only_check ^
input=chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.inp ^
user=umat_chaboche_v1_with_sdvini.f ^
datacheck interactive

if errorlevel 1 (
    echo ERROR: STATEV-only datacheck failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Case B: STATEV+stress datacheck
echo ============================================================

call abaqus job=chaboche_stage4b_statev_stress_check ^
input=chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress.inp ^
user=umat_chaboche_v1_with_sdvini.f ^
datacheck interactive

if errorlevel 1 (
    echo ERROR: STATEV+stress datacheck failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Both Stage 4B datachecks completed.
echo ============================================================
pause

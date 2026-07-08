@echo off
REM Stage 10A no-skip 100-cycle Abaqus reference.

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
echo Stage 10A datacheck: 100-cycle no-skip reference
echo ============================================================

call abaqus job=chaboche_vp_v1_cyclic_eps005_100cycles_check ^
    input=chaboche_vp_v1_cyclic_eps005_100cycles.inp ^
    user=umat_chaboche_v1_with_sdvini_sigini.f ^
    datacheck interactive scratch=.

if errorlevel 1 exit /b 1

echo.
echo ============================================================
echo Stage 10A full run: 100-cycle no-skip reference
echo ============================================================

call abaqus job=chaboche_vp_v1_cyclic_eps005_100cycles ^
    input=chaboche_vp_v1_cyclic_eps005_100cycles.inp ^
    user=umat_chaboche_v1_with_sdvini_sigini.f ^
    interactive ask_delete=OFF scratch=.

if errorlevel 1 exit /b 1

echo.
echo Stage 10A 100-cycle no-skip reference completed.

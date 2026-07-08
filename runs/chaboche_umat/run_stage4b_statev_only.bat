@echo off
REM Stage 4B Test A: STATEV-only injection
REM Runs one cycle continuation from cycle-19 state (STATEV only, no stress)
REM Expected: Will differ from explicit cycle-20 due to missing stress initialization

setlocal enabledelayedexpansion

cd /d D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat

echo Loading Intel oneAPI + Visual Studio Build Tools environment...
set "VS2022INSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64
echo.

echo ========================================
echo Stage 4B Test A: STATEV-only injection
echo ========================================
echo.
echo Job: chaboche_stage4b_cycle19_exact_to_cycle20_statev_only
echo User subroutine: umat_chaboche_v1_with_sdvini.f
echo Input deck: chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.inp
echo.
echo Testing: SDVINI initialization (no stress)
echo Expected behavior: One cycle continuation with initialized STATEV
echo Expected result: Will differ from cycle-20 baseline (stress effect)
echo.
echo Running Abaqus...
echo.

call abaqus job=chaboche_stage4b_cycle19_exact_to_cycle20_statev_only ^
        input=chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.inp ^
        user=umat_chaboche_v1_with_sdvini.f ^
        interactive ask_delete=OFF scratch=.

if !errorlevel! equ 0 (
    echo.
    echo ========================================
    echo Test A completed successfully
    echo ========================================
    echo Job name: chaboche_stage4b_cycle19_exact_to_cycle20_statev_only
    echo Output files:
    echo   - chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.odb
    echo   - chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.msg
    echo   - chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.sta
) else (
    echo.
    echo ========================================
    echo Test A FAILED with error code !errorlevel!
    echo ========================================
)

pause

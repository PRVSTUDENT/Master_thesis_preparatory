@echo off
REM Stage 4B clean STATEV-only continuation with proven SDVINI activation.

setlocal enabledelayedexpansion

cd /d D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat

echo Loading Intel oneAPI + Visual Studio Build Tools environment...
set "VS2022INSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64
echo.

echo ========================================
echo Stage 4B Clean STATEV-only continuation
echo ========================================
echo.
echo Job: chaboche_stage4b_cycle19_exact_to_cycle20_statev_only_clean
echo User subroutine: umat_chaboche_v1_with_sdvini_clean.f
echo Input deck: chaboche_stage4b_cycle19_exact_to_cycle20_statev_only_clean.inp
echo.

call abaqus job=chaboche_stage4b_cycle19_exact_to_cycle20_statev_only_clean ^
        input=chaboche_stage4b_cycle19_exact_to_cycle20_statev_only_clean.inp ^
        user=umat_chaboche_v1_with_sdvini_clean.f ^
        interactive ask_delete=OFF scratch=.

if !errorlevel! equ 0 (
    echo.
    echo Clean STATEV-only job completed successfully.
) else (
    echo.
    echo Clean STATEV-only job FAILED with error code !errorlevel!
)

pause

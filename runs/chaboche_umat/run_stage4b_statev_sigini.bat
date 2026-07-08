@echo off
REM Stage 4B STATEV + SIGINI residual-stress continuation.

setlocal enabledelayedexpansion

cd /d D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat

echo Loading Intel oneAPI + Visual Studio Build Tools environment...
set "VS2022INSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64
echo.

echo ========================================
echo Stage 4B STATEV + SIGINI continuation
echo ========================================
echo.
echo Job: chaboche_stage4b_cycle19_exact_to_cycle20_statev_sigini
echo User subroutine: umat_chaboche_v1_with_sdvini_sigini.f
echo Input deck: chaboche_stage4b_cycle19_exact_to_cycle20_statev_sigini.inp
echo.

call abaqus job=chaboche_stage4b_cycle19_exact_to_cycle20_statev_sigini ^
        input=chaboche_stage4b_cycle19_exact_to_cycle20_statev_sigini.inp ^
        user=umat_chaboche_v1_with_sdvini_sigini.f ^
        interactive ask_delete=OFF scratch=.

if !errorlevel! equ 0 (
    echo.
    echo Stage 4B STATEV + SIGINI job completed successfully.
) else (
    echo.
    echo Stage 4B STATEV + SIGINI job FAILED with error code !errorlevel!
)

pause

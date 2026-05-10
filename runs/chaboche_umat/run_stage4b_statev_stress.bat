@echo off
REM Stage 4B Test B: STATEV + Stress injection
REM Runs one cycle continuation from cycle-19 state (STATEV and stress both initialized)
REM Expected: Should closely match explicit cycle-20 (within material/numerics tolerance)

setlocal enabledelayedexpansion

cd /d D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat

echo ========================================
echo Stage 4B Test B: STATEV+Stress injection
echo ========================================
echo.
echo Job: chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress
echo User subroutine: umat_chaboche_v1_with_sdvini.f
echo Input deck: chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress.inp
echo.
echo Testing: Full state injection (SDVINI + *INITIAL CONDITIONS)
echo Residual stress: S11 = 335.577 MPa (from cycle-19)
echo Expected behavior: One cycle continuation with full state initialization
echo Expected result: Should match explicit cycle-20 closely
echo.
echo Running Abaqus...
echo.

abaqus job=chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress ^
        input=chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress.inp ^
        user=umat_chaboche_v1_with_sdvini.f ^
        interactive ask_delete=OFF scratch=cleanup

if !errorlevel! equ 0 (
    echo.
    echo ========================================
    echo Test B completed successfully
    echo ========================================
    echo Job name: chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress
    echo Output files:
    echo   - chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress.odb
    echo   - chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress.msg
    echo   - chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress.sta
) else (
    echo.
    echo ========================================
    echo Test B FAILED with error code !errorlevel!
    echo ========================================
)

pause

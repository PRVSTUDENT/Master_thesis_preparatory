@echo off
REM Stage 4B Test B2: STATEV + model-level stress injection
REM Runs one cycle continuation from cycle-19 state with STATEV and initial stress.

setlocal enabledelayedexpansion

cd /d D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat

echo Loading Intel oneAPI + Visual Studio Build Tools environment...
set "VS2022INSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64
echo.

echo ========================================
echo Stage 4B Test B2: STATEV+Stress model-level injection
echo ========================================
echo.
echo Job: chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress_modellevel
echo User subroutine: umat_chaboche_v1_with_sdvini.f
echo Input deck: chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress_modellevel.inp
echo.
echo Testing: Full state injection with model-level *INITIAL CONDITIONS, TYPE=STRESS
echo Residual stress: S11 = 335.577 MPa from cycle-19
echo Expected result: Should match explicit cycle-20 more closely than STATEV-only
echo.
echo Running Abaqus...
echo.

call abaqus job=chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress_modellevel ^
        input=chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress_modellevel.inp ^
        user=umat_chaboche_v1_with_sdvini.f ^
        interactive ask_delete=OFF scratch=.

if !errorlevel! equ 0 (
    echo.
    echo ========================================
    echo Test B2 completed successfully
    echo ========================================
    echo Job name: chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress_modellevel
    echo Output files:
    echo   - chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress_modellevel.odb
    echo   - chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress_modellevel.msg
    echo   - chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress_modellevel.sta
) else (
    echo.
    echo ========================================
    echo Test B2 FAILED with error code !errorlevel!
    echo ========================================
)

pause

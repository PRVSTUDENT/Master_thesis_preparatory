@echo off
REM Datacheck for baseline increment sensitivity deck

cd /d D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat

set "VS2022INSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64

abaqus job=chaboche_eps005_20cycles_dt_original_output_check ^
input=increment_sensitivity_study\chaboche_eps005_20cycles_dt_original_output.inp ^
user=umat\chaboche_vp_v1_working.f ^
datacheck interactive

echo.
echo ===== DATACHECK COMPLETE =====

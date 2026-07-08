@echo off
setlocal

cd /d D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat

set "VS2022INSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64

abaqus job=chaboche_vp_v1_cyclic_eps005_20cycles_exact ^
input=chaboche_vp_v1_cyclic_eps005_20cycles_exact_cycle_outputs.inp ^
user=umat\chaboche_vp_v1_working.f ^
interactive

echo.
echo Abaqus finished with ERRORLEVEL=%ERRORLEVEL%
pause

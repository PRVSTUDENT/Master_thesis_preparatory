@echo off
cd /d D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat
set "VS2022INSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64
abaqus job=chaboche_eps005_20cycles_dtmax_0p005_inc6000 input=increment_sensitivity_study\chaboche_eps005_20cycles_dtmax_0p005_inc6000.inp user=umat\chaboche_vp_v1_working.f interactive

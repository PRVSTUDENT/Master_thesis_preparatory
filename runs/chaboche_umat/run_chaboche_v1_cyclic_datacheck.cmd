@echo off
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat" -arch=amd64
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64
cd /d D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat
abaqus job=chaboche_vp_v1_cyclic_1cycle input=chaboche_vp_v1_cyclic_1cycle.inp user=umat\chaboche_vp_v1_working.f datacheck interactive

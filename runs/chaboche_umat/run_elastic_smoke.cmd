@echo off
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat" -arch=amd64
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64
cd /d D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat
abaqus job=elastic_umat_smoke input=chaboche_umat_1cycle.inp user=umat\chaboche_umat_template.f interactive

@echo off
setlocal enabledelayedexpansion
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat" -arch=amd64
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64
cd /d D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat

for %%J in (
  chaboche_vp_v1_cyclic_eps001
  chaboche_vp_v1_cyclic_eps002
  chaboche_vp_v1_cyclic_eps005
  chaboche_vp_v1_cyclic_eps010
) do (
  echo === DATACHECK %%J ===
  abaqus job=%%J input=%%J.inp user=umat\chaboche_vp_v1_working.f datacheck interactive
  echo DATACHECK_EXIT %%J !ERRORLEVEL!
  if !ERRORLEVEL! EQU 0 (
    echo === ANALYSIS %%J ===
    abaqus job=%%J input=%%J.inp user=umat\chaboche_vp_v1_working.f interactive
    echo ANALYSIS_EXIT %%J !ERRORLEVEL!
  ) else (
    echo SKIP_ANALYSIS %%J
  )
)

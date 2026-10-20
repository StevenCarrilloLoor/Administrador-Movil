@echo off
rem Atajo del Administrador Movil: el Python del .venv, aislado (-I), con los argumentos tal cual.
"%~dp0.venv\Scripts\python.exe" -I "%~dp0movil.py" %*

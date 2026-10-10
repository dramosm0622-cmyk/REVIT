@echo off
rem Ejecuta el instalador de CAD-MCP (debe estar en la misma carpeta que instalar_cad_mcp.ps1)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar_cad_mcp.ps1"

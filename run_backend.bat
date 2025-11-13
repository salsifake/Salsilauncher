@echo off
cd /d %~dp0
uvicorn backend.main:app --reload
pause
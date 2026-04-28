@echo off

REM 激活虚拟环境
echo 激活虚拟环境...
venv\Scripts\activate

REM 运行项目
echo 启动 NeuroPrime 项目...
py run.py

pause

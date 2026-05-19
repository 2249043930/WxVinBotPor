@echo off
chcp 65001 >nul
title 千寻禁止微信自动更新 By DaenQQ13301666564
color 0A

:: 检查是否以管理员身份运行
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 请以管理员身份运行此脚本。
    echo.
    echo 正在尝试自动提权...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs" >nul 2>&1
    echo.
    echo 如果未弹出 UAC 窗口，请手动右键选择"以管理员身份运行"。
    timeout /t 3 >nul
    exit /b 1
)

:: 以下为管理员权限下的操作
echo.
echo ========================================
echo     千寻禁止微信自动更新 - 已获取管理员权限
echo ========================================
echo.

:: 设置hosts文件路径
set "hosts_path=C:\Windows\System32\drivers\etc\hosts"
set "temp_file=%temp%\hosts_temp_%random%.txt"

:: 设置要添加的域名
set "domain1=dldir1.qq.com"
set "domain2=dldir1v6.qq.com"

echo 操作信息:
echo • 目标文件: %hosts_path%
echo • 将添加以下规则:
echo   127.0.0.1 %domain1%
echo   127.0.0.1 %domain2%
echo.

:: 检查域名是否已存在
echo 正在检查当前hosts文件...
echo.

findstr /C:"%domain1%" "%hosts_path%" >nul
set exist1=%errorlevel%

findstr /C:"%domain2%" "%hosts_path%" >nul
set exist2=%errorlevel%

if %exist1% equ 0 (
    echo [✓] %domain1% 已存在
) else (
    echo [ ] %domain1% 未添加
)

if %exist2% equ 0 (
    echo [✓] %domain2% 已存在
) else (
    echo [ ] %domain2% 未添加
)

if %exist1% equ 0 if %exist2% equ 0 (
    echo.
    echo ========================================
    echo 无需操作：所有域名都已存在于hosts文件中！
    echo ========================================
    echo.
	echo 按任意键退出...
	pause >nul
    exit /b 0
)

echo.
echo 正在备份原始hosts文件...
set "timestamp=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%"
set "backup_file=%hosts_path%.backup_%timestamp%"

copy "%hosts_path%" "%backup_file%" >nul 2>&1
if exist "%backup_file%" (
    echo [✓] 备份成功: %backup_file%
) else (
    echo [✗] 备份失败（可能文件不存在，将创建新文件）
)

echo.
echo 正在修改hosts文件...

:: 创建临时文件并写入内容
(
    :: 如果原文件存在，先复制内容
    if exist "%hosts_path%" (
        type "%hosts_path%"
        echo.
    )
    
    :: 添加注释和分隔线
    echo # ========================================
    echo # 千寻禁止微信自动更新 - 添加时间: %date% %time%
    echo # ========================================
    
    :: 添加需要的内容
    if %exist1% neq 0 echo 127.0.0.1 %domain1%
    if %exist2% neq 0 echo 127.0.0.1 %domain2%
    
    echo # ========================================
    echo.
) > "%temp_file%" 2>nul

:: 替换原始文件
copy "%temp_file%" "%hosts_path%" >nul 2>&1
del "%temp_file%" >nul 2>&1

if %errorlevel% equ 0 (
    echo [✓] Hosts文件修改成功！
    echo.
    
    :: 显示新增的内容
    echo 新增内容:
    echo --------------------------
    if %exist1% neq 0 echo 127.0.0.1 %domain1%
    if %exist2% neq 0 echo 127.0.0.1 %domain2%
    echo --------------------------
    echo.
    
    :: 刷新DNS缓存
    echo 正在刷新DNS缓存...
    ipconfig /flushdns >nul 2>&1
    echo [✓] DNS缓存已刷新
    echo.
    
    echo ========================================
    echo           操作完成！
    echo ========================================
    echo.
    echo 说明:
    echo 1. 已成功修改hosts文件
    echo 2. 已自动备份原文件到: %backup_file%
    echo 3. DNS缓存已刷新，修改立即生效
    echo 4. 如需恢复，请使用备份文件或手动编辑hosts文件
    echo.
    
) else (
    echo.
    echo ========================================
    echo           修改失败！
    echo ========================================
    echo 可能原因:
    echo 1. 文件权限不足
    echo 2. 文件被其他程序占用
    echo 3. 防病毒软件阻止
    echo.
    echo 请尝试手动修改文件: %hosts_path%
    echo.
)

echo.
echo 按任意键退出...
pause >nul
@echo off

::copy py file
echo "copying py file..."

rmdir /s /q D:\Python27\PyInstaller-2.1\excel_and_json\
xcopy /Y /E excel_and_json.py D:\Python27\PyInstaller-2.1\excel_and_json\
xcopy /Y /E Sheet.py D:\Python27\PyInstaller-2.1\excel_and_json\
xcopy /Y /E SheetManager.py D:\Python27\PyInstaller-2.1\excel_and_json\

echo "copying py file ok!"

pause

:: pack py file to exe file
echo "packing py file to exe...\n"

cd /D D:\Python27\PyInstaller-2.1\

python pyinstaller.py --noconfirm --windowed excel_and_json\excel_and_json.py

echo "\n"

pause

python pyinstaller.py --noconfirm excel_and_json\excel_and_json.spec

echo "\n"

pause

rmdir /s /q g:\code\Server\ExcelToJson\excel_and_json\
xcopy /Y /E D:\Python27\PyInstaller-2.1\excel_and_json\dist\excel_and_json\* g:\code\Server\ExcelToJson\excel_and_json\
xcopy /Y /E D:\Python27\PyInstaller-2.1\excel_and_json\dist\excel_and_json\* E:\GodOfWar\doc\策划案子\excel\数据表导入工具\jason\

echo "\n\n"

echo "Done!"

pause

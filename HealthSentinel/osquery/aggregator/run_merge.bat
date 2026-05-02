@echo off
python "%~dp0merge_all_complete.py" > "%~dp0merge_output.log" 2>&1
echo Done! Check merge_output.log for results
pause

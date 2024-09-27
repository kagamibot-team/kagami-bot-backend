@echo off
call ./.venv/Scripts/activate.bat

coverage run -m unittest discover
coverage html

echo ==============
echo 测试运行好了
echo 你可以往上看看哪里有问题
echo 也可以打开 .\htmlcov\index.html 查看目前的测试覆盖率
echo ==============

pause
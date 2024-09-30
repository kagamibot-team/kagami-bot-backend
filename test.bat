:: ---------------------------------------------------------------- ::
::  **Notice**:                                                     ::
::      This file is under the decoding of GB2312. If you cannot    ::
::      view the content in this file correctly in VSCode, you can  ::
::      enable "files.autoGuessEncoding" setting in VSCode.         ::
::                                                                  ::
::      I'm not going to make *this* file able to work in other     ::
::      non-Chinese computers. If you have any solution, you can    ::
::      edit this file directly or just write a Python-based script ::
::      to run tests automatically and generate the `coverage`      ::
::      reports. Thank you!                                         ::
:: ---------------------------------------------------------------- ::

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
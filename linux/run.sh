#! /bin/bash

srcdir=$(dirname "$0")

screen -dmS nonebot
screen -S nonebot -X stuff "cd \"$srcdir\"\n"
screen -S nonebot -X stuff 'cd ..\n'
screen -S nonebot -X stuff ". ./.venv/bin/activate\n"
screen -S nonebot -X stuff "python bot.py\n"

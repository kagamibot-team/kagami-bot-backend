#! /bin/bash

screen -dmS nonebot
screen -S nonebot-upgrade -X stuff 'cd "$(dirname "$0")"\n'
screen -S nonebot-upgrade -X stuff 'cd ..\n'
screen -S nonebot -X stuff ". ./.venv/bin/activate\n"
screen -S nonebot -X stuff "python bot.py\n"

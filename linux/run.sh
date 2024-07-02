#! /bin/bash

screen -dmS nonebot
screen -S nonebot -X stuff "cd /home/orangepi/passbot\n"
screen -S nonebot -X stuff ". ./.venv/bin/activate\n"
screen -S nonebot -X stuff "python bot.py\n"

#!/bin/sh

screen -dmS nonebot-upgrade
screen -S nonebot-upgrade -X stuff "cd /home/orangepi/passbot\n"
screen -S nonebot-upgrade -X stuff "git pull\n"
screen -S nonebot-upgrade -X stuff ". ./.venv/bin/activate\n"
screen -S nonebot-upgrade -X stuff "python -m pip install -r requirements.txt\n"
screen -S nonebot-upgrade -X stuff "bash ./linux/run.sh\n"
screen -S nonebot-upgrade -X stuff "exit\n"

screen -S nonebot -X quit

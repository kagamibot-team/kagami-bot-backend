# Passthem-bot

## 如何部署这个 bot

### 创建虚拟环境

首先，因为我用到了一些新特性，所以需要安装 Python 3.12 或以上的版本，并安装 `venv` 库，然后使用 `venv` 库在合适的文件夹中创建虚拟环境。

```bash
pip install virtualenv
virtualenv .venv
```

然后，激活虚拟环境。在不同的系统中，激活虚拟环境的方式不同。在 Linux 中：

```bash
source ./.venv/bin/activate
```

在 Windows 中：

```bash
.\.venv\Scripts\activate
```

### 安装需要的库

```bash
pip install 'nonebot2[fastapi]'
pip install nonebot-adapter-onebot nonebot-adapter-console nonebot_plugin_alconna nonebot-plugin-orm[sqlite]
pip install pillow opencv-python types-Pillow requests urllib3==1.26.5
```

### 配置 Bot

在项目目录中，创建 `.env` 文件。你可以填写以下内容：

```
ENVIRONMENT=dev
```

此时，将会自动挂载 `.env.dev` 中的配置项，里面是我写好了的一些配置。同样，如果要应用到生产环境，请设置：

```
ENVIRONMENT=prod
```

此时，将会自动挂载 `.env.prod` 中的配置项。

### 迁移数据库

初次运行时，需要先将本地的数据库升级到最新版本。

```bash
alembic upgrade head
```

这条命令的意思是，使用 alembic，将数据库更新到最新版本（HEAD）。

### 运行 Bot 后端

直接运行 `python bot.py` 即可。

### 选择合适的前端

由于一些原因，我不在这里放出适合的前端框架，请自行寻找。

当找到合适的前端框架以后，请将其反向 Websocket 配置为 `ws://127.0.0.1:21333/onebot/v11/ws`。

## 如何贡献

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 关于

这个 bot 目前仍在开发，不向外提供服务。

### 制作人员名单

制作人员名单（Bilibili用户名）：

- 程序：passthem
- 策划：Yscao、榆木华、Dleshers沣、阿我饿一屋雨、passthem
- 绘画：Yscao、榆木华、Dleshers沣、阿我饿一屋雨

鸣谢：wumcaT 和 芍兰bot

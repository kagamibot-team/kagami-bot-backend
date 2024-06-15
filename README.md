# Passthem-bot

## 如何部署这个 bot

### 创建虚拟环境

首先，安装 Python 3.11 以上的版本，并安装 `venv` 库，然后使用 `venv` 库在合适的文件夹中创建虚拟环境。

```bash
python -m venv ./passbot/
cd ./passbot
```

然后，激活虚拟环境。在不同的系统中，激活虚拟环境的方式不同，这里介绍 Linux 中的激活方法：

```bash
source ./bin/activate
```

### 安装需要的库

注意下面安装 `pipx` 并 `ensurepath` 之后，需要先退出虚拟环境，再进入。

```bash
pip install pipx
pipx ensurepath
pipx install nb-cli
nb adapter install nonebot-adapter-onebot
pip install nonebot-plugin-orm
```

然后，需要安装一些额外的库，我暂时没有精力整理出来，请自行安装吧！

### 建立需要的文件夹

```bash
mkdir data
cd data
mkdir catch
cd catch
mkdir awards
mkdir skins
```

### 运行 Bot 后端

```bash
nb run
```

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

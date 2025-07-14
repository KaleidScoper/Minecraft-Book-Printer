# Minecraft-Book-Printer

本项目基于B站用户[懒羊羊Tetrazole](https://space.bilibili.com/1084866085)的[项目](https://github.com/LanYangYang321/Minecraft-Book-Printer)修改而成，原本的代码存在很多问题导致可用性很差。

## 功能：
自动化将txt纯文本转化为Minecraft成书的脚本。适用于任何版本的任何书与笔，包括模组中任何类似原版书籍交互页面的可输入物品。

## 使用方法：

1. 首先下载或克隆项目源码文件到任意位置；
2. 在源码文件夹里的“input.txt”中粘贴你的文本，其中的多个空行将在输出时被合并成一个；
3. 双击“run.bat”启动脚本；
4. 进入游戏打开书与笔界面，将鼠标放在翻页按钮处；
5. 按住ctrl键（约一秒）直到看见文字被打印到书上，等待完成即可。

## 点完闪退怎么办

闪退是环境问题。本项目采用了pywin32这个一般不预装的库，需要自行安装。下面是从安装Python到一切就绪的完整教程。

1. 以管理员身份打开cmd（就是班里b哥用教室大屏打开的那个黑框）或者powershell（推荐）。
2. 复制粘贴运行下面的命令来安装包管理器choco，免去自行配置环境：
```sh
Set-ExecutionPolicy Bypass -Scope Process -Force; `
[System.Net.ServicePointManager]::SecurityProtocol = `
[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
3. 关闭此窗口然后重新打开。现在执行下面的命令安装python：
```shell
choco install python --version=3.12.2 -y
```
4. 执行下面的命令安装所需的依赖：
```shell
pip install pywin32 pyautogui pyperclip
```
5. 完成。
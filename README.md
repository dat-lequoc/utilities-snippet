# utilities-snippet
random snippets

# Powershell shortcut alias
---------------------------
Create : 
```
function Run-UnfoldScript {
    python C:\Users\quocd\Coding\unfold_claude\script.py
}

New-Alias -Name unfold -Value Run-UnfoldScript
```
Delete:
```
Remove-Item -Path Alias:unfold
```
# Find path to a python library
-------------------------
```python 
import sys

# First, ensure the library is available (you can replace 'numpy' with the library you're interested in)
library_name = 'langchain_experimental.tabular_synthetic_data.base'

if library_name in sys.modules:
    # If the library is already imported, find its path
    print(sys.modules[library_name].__file__)
else:
    # If not imported, import it and then find its path
    import importlib
    library = importlib.import_module(library_name)
    print(library.__file__)
```


# Google Drive download:
-----------------------
1. Curl Wget Extension: https://chromewebstore.google.com/detail/curlwget/dgcfkhmmpcmkikfmonjcalnjcmjcjjdn

2. Click download in the local browser

3. Click to get Wget link

# HuggingFace Login Notebook
-----------------------
```
from huggingface_hub import notebook_login
notebook_login()
```
# Clone HF model to local
-----------------------
```
apt-get install lfs-git
git init   
git lfs install   
git clone <https://huggingface.co/meta-llama/Llama-2-7b-chat-hf>
```
#Bash Utilities
---------------
```
# storage check
du -sh
```

# SSH
-----------------
It is required that your private key files are NOT accessible by others.

```
cp .ssh to ~/.ssh
chmod 600
```

# SSH - Auto install Vscode extension Remote
--------------------------------------------
https://stackoverflow.com/questions/70380724/vscode-remote-ssh-how-to-automatically-install-extensions
```
PS C:\Users\quocd> code --list-extensions
```

```
    "remote.SSH.defaultExtensions": [
        "github.copilot",
        "github.copilot-chat",
        "ms-python.debugpy",
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-toolsai.jupyter",
        "ms-toolsai.jupyter-keymap",
        "ms-toolsai.jupyter-renderers",
        "ms-toolsai.vscode-jupyter-cell-tags",
        "ms-toolsai.vscode-jupyter-slideshow",
        "vscodevim.vim",
    ],
```

# Newly installed Windows
-------------------------
App to install :
- Use Edge instead of Chrome
- Driver Booster (search serail key on youtube comment, don't download patch -> 
 virus)
- Buy a good Mouse (important for productivity)
- Wox (quick, custom search) https://www.youtube.com/watch?v=USFf2CCJEMg&ab_channel=TobieBi%E1%BA%BFtTu%E1%BB%91t
- Install WSL Ubuntu (Microsoft Store)
- Obsidian

**Good extensions**:
- Tab suspender (multi-tabs RAM optimal) 
- Winscribe (VPN)
- Dark reader
- Ads block
- Youtube Adblock
- Edge Translate

**Use Winget to install software :**  
```
winget install foxit 
winget install dropbox.dropbox 
winget install vim.vim
winget install git.git
```

**Activate script running .ps1**
(Powershell admin)
```
set-executionpolicy RemoteSigned
```

# WSL fix bugs
--------------
```
Installing, this may take a few minutes...
WslRegisterDistribution failed with error: 0x800701bc
Error: 0x800701bc WSL 2 requires an update to its kernel component. For information please visit https://aka.ms/wsl2kernel

Press any key to continue...
```
1. Search : Windows features ON/OFF
2. Enable VM, WSL
3. Restart
4. wsl.exe --update
5. Open Ubuntu WSL again => good
6.

```
sudo apt-get update && sudo apt-get upgrade
```

# WSL newly installed
---------------------
```
sudo apt-get update & sudo apt-get upgrade -y
sudo apt install nodejs npm -y
```











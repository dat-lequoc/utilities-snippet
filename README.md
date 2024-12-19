# utilities-snippet
random snippets

## Table of Contents
1. [Windows Shortcut](#windows-shortcut)
2. [Git snippets](#git-snippets)
3. [Powershell shortcut alias](#powershell-shortcut-alias)
4. [Find path to a python library](#find-path-to-a-python-library)
5. [Google Drive download](#google-drive-download)
6. [HuggingFace Login Notebook](#huggingface-login-notebook)
7. [Clone HF model to local](#clone-hf-model-to-local)
8. [Bash Utilities](#bash-utilities)
9. [SSH](#ssh)
10. [SSH - Auto install Vscode extension Remote](#ssh---auto-install-vscode-extension-remote)
11. [Newly installed Windows](#newly-installed-windows)
12. [WSL fix bugs](#wsl-fix-bugs)
13. [WSL newly installed](#wsl-newly-installed)
14. [Vim Configuration](#vim-configuration)
16. 
# Windows Shortcut
------------------
**Screenshorts**:
- Greenshot : Last region -> Shift + PrtScn

# Git snippets
--------------
```
git config --global user.name "LE Quoc Dat"
git config --global user.email "quocdat.le.insacvl@gmail.com"
git config --global credential.helper store
```

# Powershell shortcut alias
---------------------------
Open Admin Powershell.
Create PROFILE:
```
code $PROFILE
```
Copy & Paste this -> then save: 
```
function Run-UnfoldScript {
    python C:\Users\quocd\Coding\unfold_claude\script.py
}

New-Alias -Name unfold -Value Run-UnfoldScript
```
Then,
```
. $PROFILE
```
Enable running script : 
```
Set-ExecutionPolicy RemoteSigned
```


_*Option Delete:*_
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
#sudo apt install nodejs npm -y
cd
git clone https://github.com/karlin/mintty-colors-solarized.git
mv mintty-colors-solarized/ .mintty-colors-solarized/
wget https://raw.githubusercontent.com/seebi/dircolors-solarized/master/dircolors.256dark
mv dircolors.256dark .dir_colors
```
(Remember to Enter for the next command)
```
sudo apt-add-repository ppa:fish-shell/release-2
```
```
sudo apt-get update
sudo apt-get install -y fish

cat << 'EOF' >> ~/.bashrc

# Launch Fish
if [ -t 1 ]; then
  exec fish
fi

EOF

cat << 'EOF' >> ~/.config/fish/conf.d/omf.fish

# Set up colors
source ~/.mintty-colors-solarized/mintty-solarized-light.sh
eval (dircolors -c ~/.dir_colors | sed 's/>&\/dev\/null$//')

# Aliases
alias night "source ~/.mintty-colors-solarized/mintty-solarized-dark.sh"
alias day "source ~/.mintty-colors-solarized/mintty-solarized-light.sh"
EOF
```

```
curl -L http://get.oh-my.fish | fish

omf install pure
```

- Change cursor to Box:
![image](https://github.com/user-attachments/assets/d1990e5c-e131-4416-828b-4fad959c9fd2)

Final step: restart the WSL

# Vim Configuration
-------------------
1. Install `:PlugInstall`:
```
sudo apt install build-essential cmake vim-nox python3-dev -y
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
```
2. Open config .vimrc , paste the content of this file to it
```
vim ~/.vimrc
```
[https://github.com/quocdat-le-insacvl/mydotfiles/blob/master/.vimrc](https://github.com/quocdat-le-insacvl/mydotfiles/blob/master/.vimrc)

3. Type in (in vim),
Make changes
```
:source $MYVIMRC
```
Install
```
:PlugInstall
```

4. Optional : You Complete Me Plugin
```
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_current.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
sudo apt install mono-complete golang nodejs openjdk-17-jdk openjdk-17-jre npm -y

```

```
cd ~/.vim/bundle/YouCompleteMe
# OR
# cd ~/.vim/plugged/YouCompleteMe
```

```
python3 install.py --all
```
# Convert Notebook .ipynb to .pdf
```
sudo apt-get install pandoc texlive-xetex texlive-fonts-recommended texlive-plain-generic
pip install nbconvert
jupyter nbconvert --to pdf tests.ipynb
```

# Runpod init script
```
apt-get update
apt-get install -y vim

git config --global user.email "quocdat.le.insacvl@gmail.com"
git config --global user.name "LE Quoc Dat"
git config --global credential.helper store

git clone https://quocdat-le-insacvl:<token>@github.com/quocdat-le-insacvl/fast-apply-model.git

pip install huggingface_hub 
# wandb

export HUGGINGFACE_TOKEN=...
export GITHUB_TOKEN=...
export HF_HOME="/workspace/.cache/huggingface"

huggingface-cli login --token $HUGGINGFACE_TOKEN --add-to-git-credential

git clone https://github.com/kortix-ai/fast-apply
git clone https://github.com/kortix-ai/mirko

pip install unsloth
pip uninstall unsloth -y && pip install --upgrade --no-cache-dir "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
```

# Download and save HF model
```
from transformers import AutoModelForCausalLM, AutoTokenizer
model_name= "unsloth/Qwen2.5-Coder-7B-Instruct-bnb-4bit"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model.save_pretrained(model_name)
tokenizer.save_pretrained(model_name)
```

# Docker
## Install
```
sudo apt update
sudo apt upgrade -y
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker
docker --version
```

## Move default root dir Docker to /mnt/volume 
```
# Set your new location here
NEW_DOCKER_PATH="/mnt/HC_Volume_101776654" 


# Stop Docker service
sudo systemctl stop docker
sudo systemctl stop docker.socket

# Create new directory
sudo mkdir -p $NEW_DOCKER_PATH

# Copy data to new location
sudo rsync -aP /var/lib/docker/ $NEW_DOCKER_PATH/

# Backup old directory
sudo mv /var/lib/docker /var/lib/docker.old

# Create/modify daemon.json
sudo mkdir -p /etc/docker
sudo bash -c "cat > /etc/docker/daemon.json << EOL
{
    \"data-root\": \"$NEW_DOCKER_PATH\"
}
EOL"

# Start Docker service
sudo systemctl start docker
sudo systemctl start docker.socket

# Optional: Remove old directory after confirming everything works
sudo rm -rf /var/lib/docker.old

docker info | grep "Docker Root Dir"
```


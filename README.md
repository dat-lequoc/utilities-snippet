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

apt-get install git-lfs
git lfs install

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


Conda
```
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh
source ~/miniconda3/bin/activate
conda init --all


conda create -n "omni" python==3.12 -y
conda activate omni
pip install -r requirements.txt

```

Conda windows 
```
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe -o miniconda.exe
Start-Process -FilePath ".\miniconda.exe" -ArgumentList "/S" -Wait
del miniconda.exe

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


# Ubuntu 
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update -y
sudo apt install git
sudo apt install software-properties-common
PYTHON_VER=3.12
sudo apt install -y python${PYTHON_VER}

# 3. (Optional) Install pip for that version
sudo apt install -y python${PYTHON_VER}-venv python${PYTHON_VER}-distutils

# 4. Set 'python' → this Python via update‑alternatives
# Register alternatives (existing python versions get rank 1 and 2; adjust as needed)
sudo update-alternatives --install /usr/bin/python python /usr/bin/python2 1 2>/dev/null || true
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VER} 2

# 5. Optionally, make python3 also point to the new version
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3 1 2>/dev/null || true
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VER} 2

# 6. Select the default automatically
sudo update-alternatives --set python /usr/bin/python${PYTHON_VER}
sudo update-alternatives --set python3 /usr/bin/python${PYTHON_VER}

echo "Now 'python' and 'python3' point to Python ${PYTHON_VER}"
python --version
python3 --version

curl -LsSf https://astral.sh/uv/install.sh | sh

sudo apt install snapd      # if not already installed
sudo snap install --classic code

sudo apt upgrade -y
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker
docker --version

sudo systemctl daemon-reload
sudo systemctl start docker

sudo apt install vim -y
sudo apt install python3-pip -y
sudo apt remove --purge libnode-dev && sudo apt install nodejs -y
sudo apt install npm -y
```

# setup GH200 :
```
#!/usr/bin/env bash
# Installs Python 3.12, basic build deps, and PyTorch + CUDA wheels (no vLLM).
# Target: Ubuntu 22.04 with NVIDIA drivers/CUDA runtime already present (GH200-friendly).
# Usage: bash setup_torch.sh

set -euo pipefail

# Config (override via env)
: "${PY_VER:=3.12}"
: "${USE_VENV:=1}"
: "${VENV_DIR:=venv}"
# CUDA wheel tag; try cu128 (GH200) first; fall back to cu121 if needed
: "${TORCH_CUDA_TAG:=cu128}"   # options: cu128, cu121, cpu
: "${INSTALL_TRITON:=0}"       # 1 to install triton
: "${INSTALL_FLASHATTN:=0}"    # 1 to try flash-attention (Hopper/GH200)
: "${TORCH_INDEX:=https://download.pytorch.org/whl}"

if command -v nvidia-smi >/dev/null 2>&1; then
  echo "NVIDIA detected:"
  nvidia-smi || true
else
  echo "WARNING: NVIDIA drivers/CUDA runtime not detected in PATH. Continuing anyway."
fi

SUDO=""
if [ "$(id -u)" -ne 0 ]; then SUDO="sudo"; fi

export DEBIAN_FRONTEND=noninteractive

echo ">> Installing system packages..."
$SUDO apt-get update -y
$SUDO apt-get install -y software-properties-common curl git build-essential cmake ninja-build pkg-config libnuma1 git-lfs

if ! command -v python${PY_VER} >/dev/null 2>&1; then
  echo ">> Installing Python ${PY_VER}..."
  $SUDO add-apt-repository -y ppa:deadsnakes/ppa
  $SUDO apt-get update -y
  $SUDO apt-get install -y python${PY_VER} python${PY_VER}-dev python${PY_VER}-venv
fi

PY=python${PY_VER}

if ! $PY -m pip --version >/dev/null 2>&1; then
  echo ">> Installing pip for Python ${PY_VER}..."
  curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
  $PY /tmp/get-pip.py
fi

if [ "${USE_VENV}" = "1" ]; then
  echo ">> Creating venv at ${VENV_DIR}..."
  $PY -m venv "${VENV_DIR}"
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
  PY=python
fi

echo ">> Upgrading base Python packages..."
$PY -m pip install -U pip setuptools wheel packaging ninja cmake

# Hopper/GH200 arch hint for PyTorch kernels
export TORCH_CUDA_ARCH_LIST="9.0a"

install_torch() {
  local tag="${1}"
  if [ "${tag}" = "cpu" ]; then
    $PY -m pip install torch torchvision torchaudio --index-url "${TORCH_INDEX}/cpu"
  else
    $PY -m pip install torch torchvision torchaudio --index-url "${TORCH_INDEX}/${tag}"
  fi
}

set +e
echo ">> Installing PyTorch (${TORCH_CUDA_TAG})..."
install_torch "${TORCH_CUDA_TAG}"
RC=$?
set -e

if [ $RC -ne 0 ] && [ "${TORCH_CUDA_TAG}" = "cu128" ]; then
  echo ">> cu128 failed; trying cu121..."
  install_torch "cu121"
fi

if [ "${INSTALL_TRITON}" = "1" ]; then
  echo ">> Installing Triton..."
  $PY -m pip install triton
fi

if [ "${INSTALL_FLASHATTN}" = "1" ]; then
  echo ">> Installing FlashAttention (best-effort)..."
  set +e
  $PY -m pip install packaging
  # Newer FA2 provides wheels for Hopper; fallback to source if needed.
  $PY -m pip install flash-attn --no-build-isolation || {
    echo "FlashAttention wheel failed; trying source (best-effort)..."
    TMPD="$(mktemp -d)"
    git clone https://github.com/Dao-AILab/flash-attention.git "${TMPD}/flash-attention"
    pushd "${TMPD}/flash-attention/hopper" >/dev/null
    $PY setup.py install || true
    popd >/dev/null
    rm -rf "${TMPD}"
  }
  set -e
fi


echo ">> Verifying PyTorch..."
$PY - <<'PYCODE'
import sys, torch
print("Python:", sys.version)
print("Torch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
PYCODE

echo ">> Done."
```

# Connect SSH Vscode / Cursor : 
```
ssh-keygen -R 192.222.x.x && ssh ubuntu@192.222.x.x
```

# UV standalone:
```
uv add --script example.py 'requests<3' 'rich'
uv run example.py

```

# Alias :
```
echo 'alias kctrl="ps aux | grep \"ctrl-code\" | grep -v grep | awk '\''{print \$2}'\'' | xargs -r kill -9"' >> ~/.zshrc && echo 'alias acc="source .venv/bin/activate"' >> ~/.zshrc && source ~/.zshrc
echo 'uvup() { uv venv && source .venv/bin/activate && uv pip install -r "$1"; }' >> ~/.zshrc && source ~/.zshrc
echo 'runlog() { cmd=$1; shift; nohup $cmd "$@" > ${cmd}.log 2>&1 & tail -F ${cmd}.log; }' >> ~/.zshrc
```




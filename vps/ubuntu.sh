# python
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

sudo apt install python3-full -y

curl -LsSf https://astral.sh/uv/install.sh | sh

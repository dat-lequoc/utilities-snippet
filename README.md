# utilities-snippet
random snippets

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

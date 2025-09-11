curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="/root/.local/bin:$PATH" && uv --version

uv venv --python 3.12 --seed
. .venv/bin/activate
# uv pip install vllm --torch-backend=auto
uv pip install transformers accelerate torch tqdm -U


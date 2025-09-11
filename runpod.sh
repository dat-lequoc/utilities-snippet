curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="/root/.local/bin:$PATH" && uv --version

uv venv
. .venv/bin/activate
uv pip install transformers accelerate torch -U

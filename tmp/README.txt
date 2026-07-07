1. Install LiteLLM proxy
pip install 'litellm[proxy]' --break-system-packages

2. Run the proxy
litellm --config ./litellm-config.yaml --port 4000 --detailed_debug
litellm --config ./litellm-config.yaml --port 4000

@echo off
set OLLAMA_API_BASE=http://127.0.0.1:11434
aider --model ollama/qwen2.5-coder:14b --map-tokens 0

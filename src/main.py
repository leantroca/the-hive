from strands import Agent
from strands.models.ollama import OllamaModel
from strands_tools import calculator, current_time, file_read, file_write
from tools.piper_speak import piper_speak

OLLAMA_HOST = "http://localhost:11434"
# OLLAMA_LLM = "llama3.1:8b"
OLLAMA_LLM = "qwen3:14b"

ollama = OllamaModel(
	host=OLLAMA_HOST,
	model_id=OLLAMA_LLM,
)

agent = Agent(
	model=ollama,
	tools=[
		calculator,
		current_time,
		file_read,
		file_write,
		piper_speak,
	],
)
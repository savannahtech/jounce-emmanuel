import random

from models import LLMPerformance

# LLM models and metrics for simulation
LLM_MODELS = [
    "GPT-4o", "Llama 3.1 405", "Mistral Large2", "Claude 3.5 Sonnet",
    "Gemini 1.5 Pro", "GPT-4o mini", "Llama 3.1 70B", "amba 1.5Large",
    "Mixtral 8x22B", "Gemini 1.5Flash", "Claude 3 Haiku", "Llama 3.1 8B"
]

METRICS = ["TTFT", "TPS", "e2e_latency", "RPS"]

# Function to generate simulation data
def generate_simulation_data():
    data = []
    for model in LLM_MODELS:
        for metric in METRICS:
            # Generate 1000 random values for each metric
            values = [random.uniform(10, 100) for _ in range(1000)]
            for value in values:
                data.append(LLMPerformance(
                    llm_name = model,
                    metric_name = metric,
                    value = value  # Each value is added as a separate entry
                ))
    return data

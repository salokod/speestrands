import os
from strands.models import OllamaModel, BedrockModel


def get_model():
    """
    Factory function to return the appropriate LLM Model based on environment variables.
    Defaults to local Ollama if no environment variable is set.
    """
    # Look for the environment variable, default to 'ollama'
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "ollama":
        print("[System] Using Local Ollama Model (qwen2.5:14b)")
        return OllamaModel(model_id="qwen2.5:14b", host="http://192.168.30.195:11434")

    elif provider == "bedrock":
        print("[System] Using AWS Bedrock Model (Claude 3.5 Sonnet)")
        # BedrockModel will automatically pick up your AWS credentials
        # from your ~/.aws/credentials file or environment variables.
        # By default, Strands uses 'anthropic.claude-3-5-sonnet-20240620-v1:0'
        return BedrockModel()

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")

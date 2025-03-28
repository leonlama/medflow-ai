import tiktoken
import logging


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Estimate token count using tiktoken."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def log_token_count(text: str, label: str = "Input", model: str = "gpt-4o"):
    token_count = count_tokens(text, model)
    logging.info(f"[TOKEN COUNT] {label} text has {token_count} tokens")

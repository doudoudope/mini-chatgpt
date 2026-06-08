import anthropic

client = anthropic.Anthropic(
    max_retries=3,   # exponential backoff on 429s and 5xx errors
    timeout=30.0,    # hard timeout per attempt in seconds
)


def chat(history: list[dict]) -> str:
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=history,
    )
    return response.content[0].text

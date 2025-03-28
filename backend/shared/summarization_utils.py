def summarize_text(transcript: str) -> dict:
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": transcript}
    ]

    logging.info(f"[TOKEN COUNT] Input text has {len(transcript.split())} tokens")
    logging.info(f"[GPT REQUEST] Transcript (first 100 chars): {transcript[:100]}")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"},
        max_tokens=300,
        temperature=0.3
    )

    try:
        summary = json.loads(response.choices[0].message.content)
    except Exception as e:
        raise ValueError(f"Failed to parse JSON output: {str(e)}")

    is_valid, validation_msg = validate_medical_data(summary)
    if not is_valid:
        raise ValueError(validation_msg)

    return remove_empty_elements(summary)

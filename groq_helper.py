# groq_helper.py

import time
from groq import APIStatusError


DEFAULT_MAX_TOKENS = 1500


def safe_chat(
    client,
    model,
    messages,
    temperature=0.2,
    max_tokens=DEFAULT_MAX_TOKENS,
    max_retries=3,
):
    """
    Wrapper around client.chat.completions.create that:

    - Caps output tokens (so max_tokens doesn't blow the TPM budget).
    - Retries on 429 rate-limit errors, respecting the retry-after header.
    - Retries on transient 5xx errors with exponential backoff.
    """

    last_error = None

    for attempt in range(max_retries):

        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        except APIStatusError as e:

            last_error = e
            status = getattr(e, "status_code", None)

            if status == 429:
                # Rate limit — respect retry-after if present
                retry_after = 5
                try:
                    retry_after = int(
                        e.response.headers.get("retry-after", 5)
                    )
                except Exception:
                    pass

                time.sleep(retry_after + 1)

            elif status and 500 <= status < 600:
                # Transient server error — exponential backoff
                time.sleep(2 ** attempt)

            else:
                # Anything else — do not retry
                raise

    # Retries exhausted
    raise last_error
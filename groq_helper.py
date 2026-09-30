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
    response_format=None,
):
    """
    Wrapper around client.chat.completions.create that:

    - Caps output tokens.
    - Optionally enforces JSON response format.
    - Retries on 429 rate-limit errors.
    - Retries on transient 5xx errors.
    """

    last_error = None

    for attempt in range(max_retries):

        try:

            request_kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if response_format is not None:
                request_kwargs["response_format"] = response_format

            return client.chat.completions.create(
                **request_kwargs
            )

        except APIStatusError as e:

            last_error = e
            status = getattr(e, "status_code", None)

            if status == 429:

                retry_after = 5

                try:
                    retry_after = int(
                        e.response.headers.get(
                            "retry-after",
                            5
                        )
                    )
                except Exception:
                    pass

                time.sleep(retry_after + 1)

            elif status and 500 <= status < 600:

                time.sleep(2 ** attempt)

            else:

                raise

    raise last_error
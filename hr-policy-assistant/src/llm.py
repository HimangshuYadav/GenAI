"""
LLM module: Groq API client with streaming, strict system prompt enforcement,
source citation handling, automatic model fallback, and error handling.
"""
import os
from typing import List, Dict, Any, Generator, Optional
from groq import Groq, AuthenticationError, RateLimitError, APIError

from src.config import (
    GROQ_API_KEY,
    DEFAULT_GROQ_MODEL,
    HR_CONTACT_EMAIL,
    DISCLAIMER_NOTE
)

SYSTEM_PROMPT = f"""You are the official HR Policy Assistant. Your sole purpose is to answer employee questions strictly and accurately using ONLY the retrieved employee handbook excerpts provided below.

MANDATORY RULES:
1. STRICT TRUTH ONLY FROM HANDBOOK:
   - Base your answer ENTIRELY on the provided handbook text.
   - Do NOT use outside knowledge, do NOT extrapolate, and do NOT make assumptions.
   - If the handbook context does NOT explicitly answer the question, or if the question is out of scope (e.g. general knowledge, sports, unrelated topics), output EXACTLY this sentence and nothing else:
     "I couldn't find this in the employee handbook. Please contact HR at {HR_CONTACT_EMAIL}."

2. STRUCTURED FORMAT:
   - Lead with a direct, concise summary sentence (1-2 sentences).
   - Follow with key specifics in clean, structured bullet points.
   - Explicitly quote exact quantitative metrics: numbers, dollar caps, percentages, tenure thresholds, timeframes, and approval requirements.

3. SOURCE CITATIONS:
   - For every stated rule, metric, or requirement, append a citation in the exact format: `(Section Name, p. X)`.
   - Never omit the page number or section title.

4. DISCLAIMER:
   - End every substantive response with this exact note on its own line:
     "{DISCLAIMER_NOTE}"
   - (Do NOT include this disclaimer if the answer is the "couldn't find" response).

5. TONE:
   - Professional, objective, supportive, and authoritative.
"""


def build_user_prompt(query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Constructs the prompt containing retrieved handbook context chunks.
    """
    if not retrieved_chunks:
        return (
            f"User Question: {query}\n\n"
            "Retrieved Context: No relevant handbook sections were found."
        )

    context_blocks = []
    for idx, chunk in enumerate(retrieved_chunks, 1):
        sec_title = chunk.get("section_title", "Handbook")
        page_num = chunk.get("page_number", "Unknown")
        text = chunk.get("text", "").strip()
        sim = chunk.get("similarity", 0.0)
        context_blocks.append(
            f"--- [Excerpt {idx} | Section: {sec_title} | Page: {page_num} | Relevance: {sim:.2f}] ---\n{text}"
        )

    context_str = "\n\n".join(context_blocks)
    return (
        f"Retrieved Handbook Context:\n{context_str}\n\n"
        f"Employee Question: {query}\n\n"
        "Please provide an accurate answer strictly following all mandatory rules and citations."
    )


def get_groq_client(api_key: Optional[str] = None) -> Optional[Groq]:
    """
    Initializes and returns a Groq client using provided key, config key, or environment.
    """
    key = (api_key or GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")).strip()
    if not key or key == "your_groq_api_key_here":
        return None
    try:
        return Groq(api_key=key)
    except Exception:
        return None


def generate_answer_stream(
    query: str,
    retrieved_chunks: List[Dict[str, Any]],
    chat_history: Optional[List[Dict[str, str]]] = None,
    model: str = DEFAULT_GROQ_MODEL,
    api_key: Optional[str] = None
) -> Generator[str, None, None]:
    """
    Streams the LLM response token by token via the Groq API.
    Handles missing keys, model fallback, rate limits, and authentication errors gracefully.
    """
    # Fast path: If no relevant chunks retrieved at all, return not found directly
    if not retrieved_chunks:
        yield f"I couldn't find this in the employee handbook. Please contact HR at {HR_CONTACT_EMAIL}."
        return

    client = get_groq_client(api_key)

    if client is None:
        yield (
            "⚠️ **Groq API Key Not Configured**\n\n"
            "To get live answers from the LLM, please provide your Groq API key:\n"
            "1. Enter it in the **Settings Modal** under *'Groq API Key'*, OR\n"
            "2. Add `GROQ_API_KEY=gsk_...` to your `.env` file and restart the server.\n\n"
            f"*(Retrieved {len(retrieved_chunks)} relevant source passages below for reference)*"
        )
        return

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if chat_history:
        for turn in chat_history[-4:]:
            role = turn.get("role")
            content = turn.get("content")
            if role in ["user", "assistant"] and content:
                messages.append({"role": role, "content": content})

    user_content = build_user_prompt(query, retrieved_chunks)
    messages.append({"role": "user", "content": user_content})

    models_to_try = [model]
    if model != "qwen/qwen3.8-27b":
        models_to_try.append("qwen/qwen3.8-27b")

    for target_model in models_to_try:
        try:
            completion = client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=0.1,
                max_tokens=1024,
                stream=True
            )

            for chunk in completion:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
            return

        except AuthenticationError:
            yield (
                "❌ **Groq Authentication Error**: The provided API key is invalid or expired. "
                "Please verify your `GROQ_API_KEY` in `.env` or in settings."
            )
            return
        except RateLimitError:
            yield (
                "⏳ **Groq Rate Limit Exceeded**: You have temporarily reached your Groq API rate limit. "
                "Please wait a few seconds and try submitting your question again."
            )
            return
        except APIError as e:
            # If model not found, try fallback model in loop
            if "model_not_found" in str(e) and target_model != models_to_try[-1]:
                continue
            yield f"⚠️ **Groq API Service Error**: {str(e)}."
            return
        except Exception as e:
            yield f"⚠️ **Unexpected Error**: {str(e)}"
            return


def generate_answer_sync(
    query: str,
    retrieved_chunks: List[Dict[str, Any]],
    chat_history: Optional[List[Dict[str, str]]] = None,
    model: str = DEFAULT_GROQ_MODEL,
    api_key: Optional[str] = None
) -> str:
    """
    Synchronous wrapper collecting the complete streamed answer.
    """
    stream = generate_answer_stream(
        query=query,
        retrieved_chunks=retrieved_chunks,
        chat_history=chat_history,
        model=model,
        api_key=api_key
    )
    return "".join(stream)

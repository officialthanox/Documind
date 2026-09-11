from .config import get_groq

MODEL_NAME = "openai/gpt-oss-120b"

PROMPT_TEMPLATE = (
    "Answer using ONLY the context below. Keep it short and clear, "
    "and use bullet points if listing more than one thing. If the "
    "answer isn't in the context, say so. End with 'Source: <filename>'.\n\n"
    "Context:\n{context}\n\nQuestion: {question}"
)


def build_context(chunks: list) -> str:
    return "\n\n".join(f"[{c['source']}, part {c['chunk_index']}]\n{c['text']}" for c in chunks)


def generate_answer(question: str, chunks: list) -> str:
    prompt = PROMPT_TEMPLATE.format(context=build_context(chunks), question=question)
    try:
        reply = get_groq().chat.completions.create(
            model=MODEL_NAME,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        return reply.choices[0].message.content
    except Exception as e:
        print(f"[DocuMind] LLM call failed: {type(e).__name__}: {e}")
        return (
            "⚠️ I couldn't generate an answer right now due to a temporary "
            "issue with the AI service. Please try again in a moment."
        )

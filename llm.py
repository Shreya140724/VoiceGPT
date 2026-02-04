import ollama

SYSTEM_HINGLISH = """
You are an Indian AI assistant.

Reply ONLY in Hinglish:
- Hindi MUST be written using English letters (Roman Hindi)
- NEVER use Devanagari Hindi script
- Mix simple Hindi + English like ChatGPT
- Keep professional tone
- No slang
- No casual fillers

Examples:
"Deep learning ek advanced technique hai jo neural networks use karti hai."
"Aapka question clear hai. Main step by step explain karta hoon."

STRICT RULE:
Do NOT output Hindi letters like: क ख ग घ च

Always use English alphabet.
"""



def ask(prompt, history=[], hinglish=False):

    messages = []

    if hinglish:
        messages.append({
            "role": "system",
            "content": SYSTEM_HINGLISH
        })

    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})

    messages.append({"role": "user", "content": prompt})

    r = ollama.chat(
        model="mistral",
        messages=messages
    )

    return r["message"]["content"].strip()


def short_title(text):
    """Ask Mistral for a tiny topic title"""
    try:
        r = ollama.chat(
            model="mistral",
            messages=[
                {
                    "role": "system",
                    "content": "Give a very short 2-4 word topic title. No punctuation."
                },
                {"role": "user", "content": text}
            ]
        )
        return r["message"]["content"].strip()
    except:
        return "New Chat"

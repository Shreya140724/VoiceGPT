import gradio as gr
from pathlib import Path
import json, time, shutil, subprocess

from whisper_stt import transcribe
from llm import ask, short_title

ROOT = Path("data/conversations")
ROOT.mkdir(parents=True, exist_ok=True)

# ---------------- HELPERS ---------------- #

def clean(t):
    return "".join(c for c in t if c.isalnum() or c == " ").strip()

def auto_title(text):
    t = short_title(text)
    return "_".join(clean(t).split()[:3])

def list_chats():
    chats = [p.name for p in ROOT.iterdir() if p.is_dir()]
    chats.sort(key=lambda x: (ROOT/x).stat().st_mtime, reverse=True)
    return chats

def load_history(topic):
    f = ROOT/topic/"history.json"
    if f.exists():
        return json.loads(f.read_text())
    return []

def save_history(topic, hist):
    f = ROOT/topic/"history.json"
    f.write_text(json.dumps(hist, indent=2))

# ---------------- TTS ---------------- #
def speak(text,out):
    subprocess.run([
        "edge-tts",
        "--voice","en-IN-PrabhatNeural",
        "--text",text,
        "--write-media",str(out)
    ],check=True)


# ---------------- CORE ---------------- #

def voice(audio, topic, hinglish):

    if audio is None:
        return None, "", gr.update(choices=list_chats(), value=topic)

    user_text = transcribe(audio)

    if not topic:
        topic = auto_title(user_text)

    chat = ROOT/topic
    (chat/"user").mkdir(parents=True, exist_ok=True)
    (chat/"bot").mkdir(exist_ok=True)

    stamp=str(int(time.time()))
    keyword=auto_title(user_text)

    user_file=chat/"user"/f"{keyword}_{stamp}.wav"
    bot_file=chat/"bot"/f"{keyword}_{stamp}.mp3"

    shutil.copy(audio,user_file)

    hist = [] if not hinglish else load_history(topic)
    hist.append({"role":"user","content":user_text})

    reply=ask(user_text,hist,hinglish)
    hist.append({"role":"assistant","content":reply})

    save_history(topic,hist)

    speak(reply,bot_file)

    return str(bot_file),reply,gr.update(choices=list_chats(),value=topic)


def new_chat():
    return None, "", gr.update(value=None)

# ---------------- UI ---------------- #

with gr.Blocks(theme=gr.themes.Soft()) as demo:

    gr.Markdown("# 🎤 VoiceGPT (Offline)")
    gr.Markdown("### Whisper + Mistral + Natural Hinglish")

    with gr.Row():

        with gr.Column(scale=1):
            chats = gr.Radio(list_chats(), label="💬 Chats")
            new = gr.Button("➕ New Chat")
            hinglish = gr.Checkbox(label="🇮🇳 Hinglish Mode", value=False)

        with gr.Column(scale=3):

            mic = gr.Audio(
                sources=["microphone","upload"],
                type="filepath",
                label="🎙 Speak"
            )

            text = gr.Textbox(label="Assistant Reply")
            out = gr.Audio(autoplay=True, label="Assistant Voice")

    mic.change(voice, [mic, chats, hinglish], [out, text, chats])
    new.click(new_chat, None, [mic, text, chats])

demo.launch(inbrowser=True)

import asyncio, json, os, subprocess, sys
lines = json.load(open("ales/lines.json", encoding="utf-8"))
os.makedirs("ales/out", exist_ok=True)

async def edge():
    import edge_tts
    for k, t in lines.items():
        await edge_tts.Communicate(t, "tr-TR-EmelNeural", rate="-4%").save(f"ales/out/{k}.mp3")
        print("edge ok", k, flush=True)

try:
    asyncio.run(edge())
    open("ales/out/ENGINE.txt", "w").write("edge-tts tr-TR-EmelNeural")
except Exception as e:
    print("edge-tts failed:", e, flush=True)
    for f in os.listdir("ales/out"): os.remove(os.path.join("ales/out", f))
    base = "https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx"
    subprocess.run(["curl", "-sSL", "-o", "v.onnx", base], check=True)
    subprocess.run(["curl", "-sSL", "-o", "v.onnx.json", base + ".json"], check=True)
    from piper import PiperVoice
    import wave
    v = PiperVoice.load("v.onnx")
    for k, t in lines.items():
        with wave.open(f"ales/out/{k}.wav", "wb") as w:
            v.synthesize_wav(t, w)
        print("piper ok", k, flush=True)
    open("ales/out/ENGINE.txt", "w").write("piper tr_TR-dfki-medium")

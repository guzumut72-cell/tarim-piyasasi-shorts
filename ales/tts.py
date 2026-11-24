import asyncio, json, os, edge_tts
VOICE = os.environ.get("VOICE", "tr-TR-EmelNeural")
lines = json.load(open("ales/lines.json", encoding="utf-8"))
os.makedirs("ales/out", exist_ok=True)
async def main():
    for k, t in lines.items():
        await edge_tts.Communicate(t, VOICE, rate="-4%").save(f"ales/out/{k}.mp3")
        print("ok", k)
asyncio.run(main())

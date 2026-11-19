"""No-cost starter: RSS -> attributed short script -> Turkish TTS -> vertical MP4.
Not an LLM or verified viral trend detector. Human review required before publication.
"""
import hashlib
import html
import json
import os
import re
import subprocess
import tempfile
import wave
from datetime import datetime, timezone
from pathlib import Path
import feedparser
import requests
from piper import PiperVoice, SynthesisConfig
from PIL import Image, ImageDraw, ImageFont

OUT = Path('output'); OUT.mkdir(exist_ok=True)
FEEDS = [
 'https://news.google.com/rss/search?q=tar%C4%B1m+fiyatlar%C4%B1+when%3A2d&hl=tr&gl=TR&ceid=TR:tr',
 'https://news.google.com/rss/search?q=bu%C4%9Fday+g%C3%BCbre+tar%C4%B1m+when%3A2d&hl=tr&gl=TR&ceid=TR:tr',
]
items = []
for feed in FEEDS:
    try:
        response = requests.get(feed, timeout=(8, 20))
        response.raise_for_status()
        items.extend(
            item for item in feedparser.parse(response.content).entries
            if item.get('title') and item.get('link')
        )
    except requests.RequestException as error:
        print('Feed error:', error, flush=True)
if not items:
    raise RuntimeError('No news returned. Avoid generating an unsourced video.')

def clean(s):
    s = re.sub('<[^>]+>', ' ', html.unescape(s))
    return re.sub(r'\s+', ' ', s).strip()

# Transparent heuristic, not engagement or fact verification.
terms = ['fiyat', 'buğday', 'gübre', 'pamuk', 'kuraklık', 'ihracat', 'üretim', 'çiftçi']
def score(item):
    title = clean(item.get('title', '')).lower()
    return sum(2 for t in terms if t in title) + int(bool(item.get('published')))
selected = max(items, key=score)
title = clean(selected.get('title', 'Tarım gündemi'))
link = selected.get('link', '')
source = clean(selected.get('source', {}).get('title', 'Google News üzerinden haber'))
source_suffix = f' - {source}'
if title.endswith(source_suffix):
    title = title[:-len(source_suffix)]
# Do not invent supporting details: headline is explicitly attributed, not asserted as independently confirmed.
script = (f'Tarım gündeminde bugün: {title}. '
          f'Bu başlık, {source} kaynağında yer alıyor. '
          'Haberin ayrıntıları ve olası piyasa etkileri için kaynak bağlantısını inceleyin. '
          'Bu video, otomatik hazırlanmış bir haber özeti denemesidir.')
MODEL_NAME = 'tr_TR-fettah-medium'
MODEL_BASE = (
    'https://huggingface.co/rhasspy/piper-voices/resolve/'
    '320d5f7f7751a17ef6512d5c23863056c6a11c0f/tr/tr_TR/fettah/medium'
)
MODEL_FILES = {
    f'{MODEL_NAME}.onnx': '5d14d5222f36aea2b8fc8dba097fcb18dcf8f5b33e5b2aa76b5e0b44602aa8d7',
    f'{MODEL_NAME}.onnx.json': '0738ecd770d4102fa967a784ae89f64d846b1b5f104076e410c978fefa70b3e7',
}


def ensure_voice_model():
    cache = Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache') / 'tarim-shorts'
    cache.mkdir(parents=True, exist_ok=True)

    for filename, checksum in MODEL_FILES.items():
        destination = cache / filename
        if destination.is_file():
            with destination.open('rb') as existing:
                if hashlib.file_digest(existing, 'sha256').hexdigest() == checksum:
                    continue

        with tempfile.NamedTemporaryFile(dir=cache, delete=False) as temporary:
            download = Path(temporary.name)
        try:
            digest = hashlib.sha256()
            with requests.get(f'{MODEL_BASE}/{filename}', stream=True, timeout=(10, 90)) as response:
                response.raise_for_status()
                with download.open('wb') as output:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        output.write(chunk)
                        digest.update(chunk)
            if digest.hexdigest() != checksum:
                raise RuntimeError(f'Voice model checksum did not match: {filename}')
            download.replace(destination)
        finally:
            download.unlink(missing_ok=True)

    return cache / f'{MODEL_NAME}.onnx'


voice_path = OUT / 'voice.wav'
voice_engine = 'Piper (tr_TR-fettah-medium)'
voice = PiperVoice.load(ensure_voice_model())
with wave.open(str(voice_path), 'wb') as narration:
    voice.synthesize_wav(script, narration, syn_config=SynthesisConfig(length_scale=1.05))
print(f'Narration generated with {voice_engine}.', flush=True)

(OUT / 'script.txt').write_text(script, encoding='utf-8')
metadata = {
    'title': title,
    'source': source,
    'url': link,
    'published': selected.get('published'),
    'generated_utc': datetime.now(timezone.utc).isoformat(),
    'voice_engine': voice_engine,
}
(OUT / 'source.json').write_text(
    json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8'
)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(fontpath, 61); small=ImageFont.truetype(fontpath, 33)
im=Image.new('RGB',(1080,1920),(12,33,31)); d=ImageDraw.Draw(im)
d.rounded_rectangle((65,145,1015,1780),radius=45,fill=(24,62,53))
d.text((100,215),'TARIM PİYASASI',font=small,fill=(169,235,184))
words=title.split(); lines=[]; line=''
for word in words:
    trial=(line+' '+word).strip()
    if d.textbbox((0,0),trial,font=font)[2] > 850 and line:
        lines.append(line);line=word
    else: line=trial
if line: lines.append(line)
y=470
for line in lines[:11]:
    d.text((100,y),line,font=font,fill='white');y+=94
d.text((100,1580),'Kaynak: '+source[:36],font=small,fill=(207,220,210))
d.text((100,1660),'Otomatik haber özeti • Kontrol gerekli',font=small,fill=(207,220,210))
im.save(OUT/'background.png')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-loop','1','-i',str(OUT/'background.png'),'-i',str(voice_path),'-c:v','libx264','-preset','fast','-tune','stillimage','-c:a','aac','-b:a','128k','-pix_fmt','yuv420p','-shortest','-movflags','+faststart',str(OUT/'short.mp4')],check=True)
print('Generated:',OUT/'short.mp4')

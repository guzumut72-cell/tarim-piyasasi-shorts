# Tarım Piyasası Shorts

Google News RSS akışlarından Türkiye tarım gündemine ilişkin bir başlık seçer. Başlık ve kaynak bilgisiyle Türkçe seslendirmeli, 1080 × 1920 dikey MP4 üretir. Konu seçimi anahtar kelimelere dayanır. YouTube'a yükleme için videoyu indirip haber kaynağını kontrol edin.

## GitHub Actions

**Actions → Daily agriculture short → Run workflow** üzerinden elle başlatabilirsiniz. Günlük çalışma saati 07.15 UTC. GitHub yoğunluğa bağlı olarak zamanlanmış çalışmaları geciktirebilir.

Tamamlanan çalışmada **Artifacts → agriculture-short** bölümünden şu dosyaları indirebilirsiniz. Dosyalar 7 gün saklanır.

- `short.mp4` — Türkçe sesli dikey video
- `script.txt` — Seslendirme metni
- `source.json` — Haber başlığı, bağlantısı, tarih bilgisi ve kullanılan ses motoru

Azure Speech bağlantısı hazır olduğunda günlük videolarda Emel kullanılır. Elle çalıştırırken **voice** alanından Emel veya Ahmet'i seçebilirsiniz. Seslendirme metni seçilen Azure Speech kaynağına gönderilir.

Kurulumda Azure Speech **F0** kaynağının anahtarını GitHub Actions repository secret olarak `AZURE_SPEECH_KEY`, bölge kodunu Actions repository variable olarak `AZURE_SPEECH_REGION` adıyla girin. **auto** seçeneği, iki Azure değeri de boşken yerel Piper sesiyle çalışır. Haber akışlarından geçerli başlık alınamazsa çalışma hata vererek durur.

## Yerel çalıştırma

Python 3.11, FFmpeg ve DejaVu Sans gerekir.

```bash
python -m pip install -r requirements.txt
python src/make_video.py
```

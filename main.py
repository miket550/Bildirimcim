import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import time
import re

# ========== AYARLAR ==========
TELEGRAM_BOT_TOKEN = '8075438517:AAH2V8mWVH9OY1qcj3QJ6CcwmERviQpGjuA'
CHAT_ID = '944442637'

DUYURU_KAYNAKLARI = [
    {
        "ad": "F.Ü - Ana Sayfa",
        "url": "https://www.firat.edu.tr/tr/page/announcement",
        "link_taban": "https://www.firat.edu.tr",
        "duyuru_secici": ".news-card h2.title",
        "link_secici": ".news-card a",
        "tarih_secici": None,
    }
]

# ========== FLASK SERVER ==========
app = Flask('')

@app.route('/')
def home():
    return "Bot aktif"

def webserveri_baslat():
    app.run(host='0.0.0.0', port=8080)

# ========== TELEGRAM MESAJ ==========
def telegrama_gonder(mesaj, buton_linki=None):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
        'text': mesaj,
        'parse_mode': 'HTML'
    }
    if buton_linki:
        data['reply_markup'] = '{"inline_keyboard":[[{"text":"Duyuruya Git", "url":"' + buton_linki + '"}]]}'
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("❗ Telegram mesajı gönderilemedi:", e)

# ========== DUYURU GETİR ==========
def duyurulari_kontrol_et():
    for kaynak in DUYURU_KAYNAKLARI:
        try:
            response = requests.get(kaynak['url'], verify=False, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Duyuru başlığı ve linki
            baslik_tag = soup.select_one(kaynak["duyuru_secici"])
            link_tag = soup.select_one(kaynak["link_secici"])

            baslik = baslik_tag.get_text(strip=True) if baslik_tag else "Başlık bulunamadı"
            link = link_tag['href'] if link_tag else None

            if link and not link.startswith("http"):
                link = kaynak["link_taban"] + link

            mesaj = f"<b>{kaynak['ad']}</b>\n{baslik}"
            if baslik != "Başlık bulunamadı":
                telegrama_gonder(mesaj, link)
                print("✅ Bildirim gönderildi:", baslik)
            else:
                print("⚠️ Başlık bulunamadı:", kaynak['ad'])

        except Exception as e:
            print(f"❌ Hata ({kaynak['ad']}):", e)

# ========== BAŞLAT ==========
print("🚀 Bot başlatıldı.")
t = Thread(target=webserveri_baslat)
t.start()

duyurulari_kontrol_et()

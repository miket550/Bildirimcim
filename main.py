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
    },
    {
        "ad": "F.Ü - Mühendislik Fakültesi",
        "url": "https://muhendislikf.firat.edu.tr/announcements-all",
        "link_taban": "https://muhendislikf.firat.edu.tr",
        "duyuru_secici": "div.new-section-detail-title h3",
        "link_secici": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "tarih_secici": "div.new-section-detail-date p",
    },
    {
        "ad": "F.Ü - İİBF",
        "url": "https://iibf.firat.edu.tr/announcements-all",
        "link_taban": "https://iibf.firat.edu.tr",
        "duyuru_secici": "div.new-section-detail-title h3",
        "link_secici": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "tarih_secici": "div.new-section-detail-date p",
    },
    {
        "ad": "F.Ü - Teknoloji Fakültesi",
        "url": "https://teknolojif.firat.edu.tr/announcements-all",
        "link_taban": "https://teknolojif.firat.edu.tr",
        "duyuru_secici": "div.new-section-detail-title h3",
        "link_secici": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "tarih_secici": "div.new-section-detail-date p",
    },
    {
        "ad": "F.Ü - Öğrenci DB",
        "url": "https://ogrencidb.firat.edu.tr/announcements-all",
        "link_taban": "https://ogrencidb.firat.edu.tr",
        "duyuru_secici": "div.new-section-detail-title h3",
        "link_secici": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "tarih_secici": "div.new-section-detail-date p",
    },
    {
        "ad": "F.Ü - Öğrenci Dekanlığı",
        "url": "https://ogrencidekanligi.firat.edu.tr/announcements-all",
        "link_taban": "https://ogrencidekanligi.firat.edu.tr",
        "duyuru_secici": "div.new-section-detail-title h3",
        "link_secici": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "tarih_secici": "div.new-section-detail-date p",
    },
    {
        "ad": "F.Ü - Yaz Okulu",
        "url": "https://yazokuluyeni.firat.edu.tr/announcements-all",
        "link_taban": "https://yazokuluyeni.firat.edu.tr",
        "duyuru_secici": "div.new-section-detail-title h3",
        "link_secici": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "tarih_secici": "div.new-section-detail-date p",
    },
    {
        "ad": "F.Ü - Eğitim Fakültesi",
        "url": "https://egitimf.firat.edu.tr/tr/announcements-all",
        "link_taban": "https://egitimf.firat.edu.tr",
        "duyuru_secici": "div.new-section-detail-title h3",
        "link_secici": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "tarih_secici": "div.new-section-detail-date p",
    },
    {
        "ad": "F.Ü - Kütüphane DB",
        "url": "https://kutuphanedb.firat.edu.tr/announcements-all",
        "link_taban": "https://kutuphanedb.firat.edu.tr",
        "duyuru_secici": "div.new-section-detail-title h3",
        "link_secici": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "tarih_secici": "div.new-section-detail-date p",
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

            baslik_tag = soup.select_one(kaynak["duyuru_secici"])
            link_tag = soup.select_one(kaynak["link_secici"])

            baslik = baslik_tag.get_text(strip=True) if baslik_tag else "Başlık bulunamadı"
            link = link_tag['href'] if link_tag else None

            if link and not link.startswith("http"):
                link = kaynak["link_taban"] + link

            tarih = "Tarih bulunamadı"
            if kaynak.get("tarih_secici"):
                detay_response = requests.get(link, verify=False, timeout=10)
                detay_soup = BeautifulSoup(detay_response.text, 'html.parser')
                tarih_tag = detay_soup.select_one(kaynak["tarih_secici"])
                if tarih_tag:
                    tarih = ''.join([s.strip() for s in tarih_tag.contents if isinstance(s, str)]).replace('\n', '').replace(' ', '')

            mesaj = f"<b>{kaynak['ad']}</b>\n{baslik}\n📅 {tarih}"
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

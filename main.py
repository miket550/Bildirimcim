import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import time
import re

# ====== AYARLAR ======
TELEGRAM_BOT_TOKEN = '8075438517:AAH2V8mWVH9OY1qcj3QJ6CcwmERviQpGjuA'
CHAT_ID = '944442637'
SURE = 120  # 2 dakika

SITELER = [
    {
        "isim": "F.Ü - Ana Sayfa",
        "ana_sayfa": "https://www.firat.edu.tr/tr",
        "duyuru_url": "https://www.firat.edu.tr/tr/page/announcement",
        "base": "https://www.firat.edu.tr",
        "baslik_secici": "h2.title",
        "tarih_secici": ".news-date"
    },
    {
        "isim": "F.Ü - İİBF",
        "ana_sayfa": "https://iibf.firat.edu.tr",
        "duyuru_url": "https://iibf.firat.edu.tr/announcements-all",
        "base": "https://iibf.firat.edu.tr",
        "baslik_secici": "div.new-section-detail-title h3",
        "tarih_secici": "div.new-section-detail-date p"
    },
    {
        "isim": "F.Ü - Mühendislik",
        "ana_sayfa": "https://muhendislikf.firat.edu.tr",
        "duyuru_url": "https://muhendislikf.firat.edu.tr/announcements-all",
        "base": "https://muhendislikf.firat.edu.tr",
        "baslik_secici": "div.new-section-detail-title h3",
        "tarih_secici": "div.new-section-detail-date p"
    },
    {
        "isim": "F.Ü - Teknoloji Fakültesi",
        "ana_sayfa": "https://teknolojif.firat.edu.tr",
        "duyuru_url": "https://teknolojif.firat.edu.tr/announcements-all",
        "base": "https://teknolojif.firat.edu.tr",
        "baslik_secici": "div.new-section-detail-title h3",
        "tarih_secici": "div.new-section-detail-date p"
    },
    {
        "isim": "F.Ü - Öğrenci DB",
        "ana_sayfa": "https://ogrencidb.firat.edu.tr",
        "duyuru_url": "https://ogrencidb.firat.edu.tr/announcements-all",
        "base": "https://ogrencidb.firat.edu.tr",
        "baslik_secici": "div.new-section-detail-title h3",
        "tarih_secici": "div.new-section-detail-date p"
    },
    {
        "isim": "F.Ü - Öğrenci Dekanlığı",
        "ana_sayfa": "https://ogrencidekanligi.firat.edu.tr",
        "duyuru_url": "https://ogrencidekanligi.firat.edu.tr/announcements-all",
        "base": "https://ogrencidekanligi.firat.edu.tr",
        "baslik_secici": "div.new-section-detail-title h3",
        "tarih_secici": "div.new-section-detail-date p"
    },
    {
        "isim": "F.Ü - Yaz Okulu",
        "ana_sayfa": "https://yazokuluyeni.firat.edu.tr",
        "duyuru_url": "https://yazokuluyeni.firat.edu.tr/announcements-all",
        "base": "https://yazokuluyeni.firat.edu.tr",
        "baslik_secici": "div.new-section-detail-title h3",
        "tarih_secici": "div.new-section-detail-date p"
    },
    {
        "isim": "F.Ü - Eğitim Fakültesi",
        "ana_sayfa": "https://egitimf.firat.edu.tr/tr",
        "duyuru_url": "https://egitimf.firat.edu.tr/tr/announcements-all",
        "base": "https://egitimf.firat.edu.tr",
        "baslik_secici": "div.new-section-detail-title h3",
        "tarih_secici": "div.new-section-detail-date p"
    },
    {
        "isim": "F.Ü - Kütüphane",
        "ana_sayfa": "https://kutuphanedb.firat.edu.tr",
        "duyuru_url": "https://kutuphanedb.firat.edu.tr/announcements-all",
        "base": "https://kutuphanedb.firat.edu.tr",
        "baslik_secici": "div.new-section-detail-title h3",
        "tarih_secici": "div.new-section-detail-date p"
    },
]

kayitli_linkler = {}

app = Flask('')

@app.route('/')
def home():
    return "Bot aktif"

def webserveri_baslat():
    app.run(host='0.0.0.0', port=8080)

def telegrama_gonder(mesaj, buton_linki=None):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
        'text': mesaj,
        'parse_mode': 'HTML'
    }
    if buton_linki:
        data['reply_markup'] = '{"inline_keyboard":[[{"text":"Duyuruya Git", "url":"' + buton_linki + '"}]]}'
    requests.post(url, data=data)

def duyurulari_kontrol_et():
    for site in SITELER:
        try:
            r = requests.get(site["duyuru_url"], timeout=10, verify=False)
            soup = BeautifulSoup(r.text, 'html.parser')
            duyurular = soup.select('a[href*="announcements-detail"]')
            if not duyurular:
                print(f"⚠️ Duyuru bulunamadı: {site['isim']}")
                continue

            ilk_duyuru = duyurular[0]
            link = ilk_duyuru.get("href")
            if not link.startswith("http"):
                link = site["base"] + link

            if kayitli_linkler.get(site["isim"]) == link:
                continue
            kayitli_linkler[site["isim"]] = link

            detay_html = requests.get(link, verify=False).text
            detay_soup = BeautifulSoup(detay_html, "html.parser")

            # Başlık
            baslik_tag = detay_soup.select_one(site["baslik_secici"])
            baslik = baslik_tag.get_text(strip=True) if baslik_tag else "Başlık bulunamadı"

            # Tarih
            tarih_tag = detay_soup.select_one(site["tarih_secici"])
            if tarih_tag:
                tarih = ''.join(tarih_tag.stripped_strings).replace("\n", "").replace(" ", "")
            else:
                tarih = "Tarih bulunamadı"

            mesaj = f"<b>{site['isim']}</b>\n{baslik}\n📅 {tarih}"
            telegrama_gonder(mesaj, link)
            print(f"📨 Gönderildi: {site['isim']}")

        except Exception as e:
            print(f"❌ HATA ({site['isim']}):", e)

def donguyu_baslat():
    while True:
        duyurulari_kontrol_et()
        time.sleep(SURE)

print("🚀 Bot başlatıldı.")
t1 = Thread(target=webserveri_baslat)
t1.start()

t2 = Thread(target=donguyu_baslat)
t2.start()

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import json
import os

# ==== AYARLAR ====
TELEGRAM_BOT_TOKEN = '8075438517:AAH2V8mWVH9OY1qcj3QJ6CcwmERviQpGjuA'
CHAT_ID = '944442637'
DEPOLAMA_DOSYASI = 'kayitli_duyurular.json'

DUYURU_KAYNAKLARI = [
    {
        "url": "https://www.firat.edu.tr/tr/page/announcement",
        "site": "F.Ü - Ana Sayfa",
        "baslik_selector": 'h2.title',
        "tarih_selector": 'span.date'
    },
    {
        "url": "https://iibf.firat.edu.tr/announcements-all",
        "site": "F.Ü - İİBF",
        "baslik_selector": 'div.new-section-detail-title h3',
        "tarih_selector": 'div.new-section-detail-date p'
    },
    {
        "url": "https://muhendislikf.firat.edu.tr/announcements-all",
        "site": "F.Ü - Mühendislik Fakültesi",
        "baslik_selector": 'div.new-section-detail-title h3',
        "tarih_selector": 'div.new-section-detail-date p'
    },
    {
        "url": "https://teknolojif.firat.edu.tr/announcements-all",
        "site": "F.Ü - Teknoloji Fakültesi",
        "baslik_selector": 'div.new-section-detail-title h3',
        "tarih_selector": 'div.new-section-detail-date p'
    },
    {
        "url": "https://ogrencidb.firat.edu.tr/announcements-all",
        "site": "F.Ü - Öğrenci İşleri",
        "baslik_selector": 'div.new-section-detail-title h3',
        "tarih_selector": 'div.new-section-detail-date p'
    },
    {
        "url": "https://ogrencidekanligi.firat.edu.tr/announcements-all",
        "site": "F.Ü - Öğrenci Dekanlığı",
        "baslik_selector": 'div.new-section-detail-title h3',
        "tarih_selector": 'div.new-section-detail-date p'
    },
    {
        "url": "https://yazokuluyeni.firat.edu.tr/announcements-all",
        "site": "F.Ü - Yaz Okulu",
        "baslik_selector": 'div.new-section-detail-title h3',
        "tarih_selector": 'div.new-section-detail-date p'
    },
    {
        "url": "https://egitimf.firat.edu.tr/tr/announcements-all",
        "site": "F.Ü - Eğitim Fakültesi",
        "baslik_selector": 'div.new-section-detail-title h3',
        "tarih_selector": 'div.new-section-detail-date p'
    },
    {
        "url": "https://kutuphanedb.firat.edu.tr/announcements-all",
        "site": "F.Ü - Kütüphane",
        "baslik_selector": 'div.new-section-detail-title h3',
        "tarih_selector": 'div.new-section-detail-date p'
    }
]

# === Web Sunucusu (Render canlı tutmak için) ===
app = Flask('')

@app.route('/')
def home():
    return "Bot çalışıyor."

def webserveri_baslat():
    app.run(host='0.0.0.0', port=8080)

# === Telegram mesaj gönder ===
def telegrama_gonder(mesaj, buton_linki=None):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
        'text': mesaj,
        'parse_mode': 'HTML'
    }
    if buton_linki:
        data['reply_markup'] = json.dumps({
            'inline_keyboard': [[{'text': 'Duyuruya Git', 'url': buton_linki}]]
        })
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram gönderim hatası:", e)

# === Kaydedilen duyuruları yükle/kaydet ===
def yukle_kayitli_duyurular():
    if os.path.exists(DEPOLAMA_DOSYASI):
        with open(DEPOLAMA_DOSYASI, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def kaydet_kayitli_duyurular(data):
    with open(DEPOLAMA_DOSYASI, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === Ana işlev: Tüm siteleri kontrol et ===
def kontrol_et():
    kayitli = yukle_kayitli_duyurular()

    for kaynak in DUYURU_KAYNAKLARI:
        site_url = kaynak["url"]
        site_adi = kaynak["site"]
        baslik_sel = kaynak["baslik_selector"]
        tarih_sel = kaynak["tarih_selector"]

        try:
            res = requests.get(site_url, timeout=10, verify=False)
            soup = BeautifulSoup(res.text, 'html.parser')

            link_etiket = soup.select_one('a[href*="announcements-detail"], a[href*="document?"]')
            if not link_etiket:
                print(f"[{site_adi}] ⛔ Duyuru linki bulunamadı.")
                continue

            link = link_etiket.get("href", "")
            if not link.startswith("http"):
                ana_sayfa = site_url.split("/announcements")[0]
                link = ana_sayfa + link

            if kayitli.get(site_adi) == link:
                print(f"[{site_adi}] ✅ Yeni duyuru yok.")
                continue

            # Duyuru sayfasına git
            detay = requests.get(link, timeout=10, verify=False)
            detay_soup = BeautifulSoup(detay.text, 'html.parser')

            baslik = detay_soup.select_one(baslik_sel)
            baslik = baslik.get_text(strip=True) if baslik else "Başlık bulunamadı"

            tarih = detay_soup.select_one(tarih_sel)
            if tarih:
                tarih = ''.join([s.strip() for s in tarih.contents if isinstance(s, str)]).replace('\n', '').replace(' ', '')
            else:
                tarih = "Tarih bulunamadı"

            mesaj = f"<b>{site_adi}</b>\n{baslik}\n📅 {tarih}"
            telegrama_gonder(mesaj, link)
            kayitli[site_adi] = link
            print(f"[{site_adi}] 🚀 Yeni duyuru gönderildi.")

        except Exception as e:
            print(f"[{site_adi}] ❗ Hata: {e}")

    kaydet_kayitli_duyurular(kayitli)

# === Başlat ===
print("🚀 Bot başlatıldı.")
t = Thread(target=webserveri_baslat)
t.start()

kontrol_et()

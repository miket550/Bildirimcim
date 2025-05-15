import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import re
import os

# ========== AYARLAR ==========
TELEGRAM_BOT_TOKEN = '8075438517:AAH2V8mWVH9OY1qcj3QJ6CcwmERviQpGjuA'
CHAT_ID = '944442637'
KAYIT_DOSYASI = 'kayitli_duyurular.txt'

SITELER = [
    {
        'ad': 'F.Ü - Ana Sayfa',
        'duyuru_url': 'https://www.firat.edu.tr/tr/page/announcement',
        'ana_sayfa': 'https://www.firat.edu.tr',
        'baslik_secici': 'h2.title',
        'tarih_secici': 'div.date',
    },
    {
        'ad': 'F.Ü - İİBF',
        'duyuru_url': 'https://iibf.firat.edu.tr/announcements-all',
        'ana_sayfa': 'https://iibf.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p',
    },
    {
        'ad': 'F.Ü - Mühendislik Fakültesi',
        'duyuru_url': 'https://muhendislikf.firat.edu.tr/announcements-all',
        'ana_sayfa': 'https://muhendislikf.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p',
    },
    {
        'ad': 'F.Ü - Teknoloji Fakültesi',
        'duyuru_url': 'https://teknolojif.firat.edu.tr/announcements-all',
        'ana_sayfa': 'https://teknolojif.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p',
    },
    {
        'ad': 'F.Ü - Öğrenci İşleri',
        'duyuru_url': 'https://ogrencidb.firat.edu.tr/announcements-all',
        'ana_sayfa': 'https://ogrencidb.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p',
    },
    {
        'ad': 'F.Ü - Öğrenci Dekanlığı',
        'duyuru_url': 'https://ogrencidekanligi.firat.edu.tr/announcements-all',
        'ana_sayfa': 'https://ogrencidekanligi.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p',
    },
    {
        'ad': 'F.Ü - Yaz Okulu',
        'duyuru_url': 'https://yazokuluyeni.firat.edu.tr/announcements-all',
        'ana_sayfa': 'https://yazokuluyeni.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p',
    },
    {
        'ad': 'F.Ü - Eğitim Fakültesi',
        'duyuru_url': 'https://egitimf.firat.edu.tr/tr/announcements-all',
        'ana_sayfa': 'https://egitimf.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p',
    },
    {
        'ad': 'F.Ü - Kütüphane',
        'duyuru_url': 'https://kutuphanedb.firat.edu.tr/announcements-all',
        'ana_sayfa': 'https://kutuphanedb.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p',
    },
]

# ========== FLASK SUNUCU ==========
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
        print("❌ Mesaj gönderilemedi:", e)

# ========== KAYIT İŞLEMLERİ ==========
def duyuru_kayitli_mi(link):
    if not os.path.exists(KAYIT_DOSYASI):
        return False
    with open(KAYIT_DOSYASI, 'r', encoding='utf-8') as f:
        return link in f.read()

def duyuru_kaydet(link):
    with open(KAYIT_DOSYASI, 'a', encoding='utf-8') as f:
        f.write(link + '\n')

# ========== DUYURULARI KONTROL ET ==========
def duyurulari_kontrol_et():
    for site in SITELER:
        try:
            response = requests.get(site['duyuru_url'], timeout=10, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            duyurular = soup.select('a[href*="announcements-detail"]')
            if not duyurular:
                print(f"⚠️ {site['ad']} - Duyuru bulunamadı.")
                continue

            link = duyurular[0]['href']
            if not link.startswith('http'):
                link = site['ana_sayfa'].rstrip('/') + '/' + link.lstrip('/')

            if duyuru_kayitli_mi(link):
                continue

            detay = requests.get(link, verify=False)
            detay_soup = BeautifulSoup(detay.text, 'html.parser')

            baslik_tag = detay_soup.select_one(site['baslik_secici'])
            baslik = baslik_tag.get_text(strip=True) if baslik_tag else 'Başlık bulunamadı'

            tarih_tag = detay_soup.select_one(site['tarih_secici'])
            if tarih_tag:
                tarih = ''.join(re.findall(r'\d+', tarih_tag.get_text()))
                if len(tarih) >= 8:
                    tarih = f"{tarih[-8:-6]}.{tarih[-6:-4]}.{tarih[-4:]}"
                else:
                    tarih = tarih_tag.get_text(strip=True).replace('\n', '').replace('\r', '').replace(' ', '')
            else:
                tarih = "Tarih bulunamadı"

            mesaj = f"<b>{site['ad']}</b>\n{baslik}\n📅 {tarih}"
            telegrama_gonder(mesaj, link)
            duyuru_kaydet(link)
            print(f"✅ Bildirim gönderildi: {site['ad']}")

        except Exception as e:
            print(f"❗ HATA ({site['ad']}):", e)

# ========== BAŞLAT ==========
print("🚀 Bot başlatıldı.")
t = Thread(target=webserveri_baslat)
t.start()

duyurulari_kontrol_et()

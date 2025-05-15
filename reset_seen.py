import os

try:
    os.remove("seen_announcements.json")
    print("✅ Kayıtlı tüm duyurular sıfırlandı.")
except FileNotFoundError:
    print("ℹ️ Zaten kayıt dosyası yoktu, işlem tamam.")
except Exception as e:
    print("❌ Sıfırlama sırasında hata oluştu:", e)

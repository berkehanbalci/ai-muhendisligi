import requests
import os
import pandas as pd
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine
from datetime import datetime
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def hava_durumu_getir(sehirler):
    print("[EXTRACT] VERİ ÇEKİLİYOR....")
    sonuclar = []

    for sehir_adi in sehirler:
        try:
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_yanit = requests.get(geo_url, params={"name": sehir_adi, "count": 1})
            geo_veri = geo_yanit.json()

            if "results" not in geo_veri or len(geo_veri["results"]) == 0:
                print(f"[EXTRACT] UYARI: '{sehir_adi}'  bulunamadı, atlanıyor")
                continue

            konum = geo_veri["results"][0]

            hava_url = "https://api.open-meteo.com/v1/forecast"
            hava_yanit = requests.get(hava_url, params ={
                "latitude": konum["latitude"],
                "longitude": konum["longitude"],
                "current": "temperature_2m,wind_speed_10m,relative_humidity_2m"
            })

            hava = hava_yanit.json()["current"]

            sonuclar.append({
                "sehir": sehir_adi,
                "sicaklik_c": hava["temperature_2m"],
                "ruzgar": hava["wind_speed_10m"],
                "nem": hava["relative_humidity_2m"]
            })
        except Exception as hata:
            print(f"[EXTRACT] HATA: '{sehir_adi}' için veri alınamadı: {hata}")
            continue
    print(f"[EXTRACT] {len(sonuclar)} şehir başarıyla çekildi")
    return sonuclar

def transform(sonuclar):
    """Veriyi dönüştürür: Fahrenheit ekler, kategori belirler, zaman damgası ekler"""
    print("[TRANSFORM] Veri dönüştürülüyor...")

    for kayit in sonuclar:
        sicaklik_c = kayit["sicaklik_c"]
        kayit["sicaklik_f"] = (sicaklik_c * 9/5) + 32
        if sicaklik_c < 15:
            kayit["kategori"] = "Soğuk"
        elif sicaklik_c < 25:
            kayit["kategori"] = "Ilık"
        else:
            kayit["kategori"] = "Sıcak"
        kayit["cekilme_zamani"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("[TRANSFORM] Tamamlandı")
    return sonuclar

    
    
    
def veritabanina_kaydet(sonuclar):
    """Veriyi PostgreSQL'e yükler"""
    print("[LOAD] PostgreSQL'e yükleniyor...")

    df = pd.DataFrame(sonuclar)

    engine = create_engine(
        f"postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}"
        f"@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv('DB_NAME')}"
    )

    df.to_sql("hava_durumu_log", engine, if_exists= "append", index = False)

    print(f"[LOAD] {len(df)} satır yüklendi")

def pipeline_calistir(sehirler):
    """Tam ETL akışını çalıştırır"""
    print("=" * 40)
    print("ETL PIPELINE BAŞLIYOR")
    print("=" * 40)

    ham = hava_durumu_getir(sehirler)
    donusturulmus = transform(ham)
    veritabanina_kaydet(donusturulmus)

    print("=" * 40)
    print("PIPELINE TAMAMLANDI")
    print("=" * 40)
    return pd.DataFrame(donusturulmus)



tools = [
    {
        "type": "function",
        "function": {
            "name": "hava_durumu_getir",
            "description": "Bir veya birden fazla şehrin güncel hava durumunu getirir (sadece okur, kaydetmez)",
            "parameters": {
                "type": "object",
                "properties": {
                    "sehirler": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Hava durumu öğrenilecek şehir isimlerinin listesi"
                    }
                },
                "required": ["sehirler"]
            }
        }
    }
]   

if __name__ == "__main__":
    sehirler = ["Ankara", "İstanbul", "İzmir", "Antalya", "Trabzon"]
    sonuc = pipeline_calistir(sehirler)
    print(sonuc)

print("\n" + "="*40)
print("AI TOOL USE TESTİ")
print("="*40)

mesajlar = [
    {"role": "user", "content": "Ankara ve İzmir hava durumu nasıl?"}
]

yanit = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages = mesajlar,
    tools=tools,
    tool_choice="auto"
)

ai_mesaji = yanit.choices[0].message
print("--- AI'ın cevabı (ham) ---")
print(ai_mesaji)

if ai_mesaji.tool_calls:
    print("\n--- AI bir araç çağırmak istiyor! ---")
    for tool_call in ai_mesaji.tool_calls:
        print(f"Fonksiyon: {tool_call.function.name}")
        print(f"Parametreler: {tool_call.function.arguments}")

if ai_mesaji.tool_calls:
    mesajlar.append(ai_mesaji)

    for tool_call in ai_mesaji.tool_calls:

        parametreler = json.loads(tool_call.function.arguments)

        sonuc = hava_durumu_getir(parametreler["sehirler"])

        mesajlar.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(sonuc, ensure_ascii = False)
        }) 


    final_yanit = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=mesajlar
    )
    print("\n--- AI'ın DOĞAL, FİNAL cevabı ---")
    print(final_yanit.choices[0].message.content)       


import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def urun_analizi(yorum):
    yanit = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system", 
                "content": """Sen bir ürün yorumu analiz uzmanısın. 
                Kullanıcının yorumunu analiz et ve SADECE aşağıdaki JSON formatında cevap ver, başka hiçbir şey yazma:
            {"duygu": "Pozitif/Negatif/Nötr", "puan": 1-5 arası bir sayı, "ozet": "yorumun 5 kelimelik özeti"}"""
            },
            {"role": "user", "content": yorum}
        ]
    )
    return yanit.choices[0].message.content


yorum = "Ürün gayet kaliteli ama kargo çok geç geldi, biraz canımı sıktı."
sonuc_metin = urun_analizi(yorum)
print("--- Ham AI cevabı ---")
print(sonuc_metin)


sonuc_json = json.loads(sonuc_metin)
print("--- Python sözlüğüne çevrildi ---")
print(sonuc_json)
print(f"Duygu: {sonuc_json['duygu']}")
print(f"Puan: {sonuc_json['puan']}")    
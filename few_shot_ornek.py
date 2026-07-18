import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def duygu_analizi(yorum):
    yanit = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages= [
            {"role": "user", "content": "Bu ürün harika, çok memnun kaldım!"},
            {"role": "assistant", "content": "Pozitif"},
            
            {"role": "user", "content": "Kargo çok geç geldi, hiç memnun kalmadım."},
            {"role": "assistant", "content": "Negatif"},
            
            {"role": "user", "content": "Ürün fena değil, idare eder."},
            {"role": "assistant", "content": "Nötr"},
            
            {"role": "user", "content": yorum}
        ]
    )
    return yanit.choices[0].message.content

yorumlar = [
    "Kesinlikle tavsiye ederim, çok kaliteli!",
    "Param boşa gitti, hiç beğenmedim.",
    "Standart bir ürün, beklediğim gibi."
]

for yorum in yorumlar:
    sonuc = duygu_analizi(yorum)
    print(f"Yorum: '{yorum}' → Duygu: {sonuc}")
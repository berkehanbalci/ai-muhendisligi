import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

yanit = client.chat.completions.create(
    model ="llama-3.3-70b-versatile",
    messages =[
        {"role": "user", "content": "Merhaba! Kendini kısaca tanıtır mısın?"}
    ]
)

print(yanit.choices[0].message.content)

mesajlar = [
    {"role": "user", "content": "Python'da liste ile tuple arasındaki fark nedir? Tek cümleyle söyle."}
]

yanit1 = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=mesajlar
)
cevap1 = yanit1.choices[0].message.content
print("AI:", cevap1)


mesajlar.append({"role": "assistant", "content": cevap1})

# Yeni bir soru sor (öncekine referans vererek)
mesajlar.append({"role": "user", "content": "Peki hangi durumda tuple tercih edilir?"})

yanit2 = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=mesajlar
)
print("AI:", yanit2.choices[0].message.content)


# ============ SYSTEM MESSAGE KARŞILAŞTIRMASI ============

# 1. Sistem mesajı OLMADAN
print("--- Sistem mesajı YOK ---")
yanit_a = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "Python nedir?"}
    ]
)
print(yanit_a.choices[0].message.content)

print("\n" + "="*50 + "\n")

# 2. Sistem mesajı İLE (5 yaşındaki çocuğa anlatır gibi)
print("--- Sistem mesajı VAR (5 yaşına anlat) ---")
yanit_b = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "Sen 5 yaşındaki bir çocuğa her şeyi çok basit, eğlenceli benzetmelerle anlatan bir öğretmensin. Kısa cevaplar ver."},
        {"role": "user", "content": "Python nedir?"}
    ]
)
print(yanit_b.choices[0].message.content)
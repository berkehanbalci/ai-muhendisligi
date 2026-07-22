# AI Mühendisliği — LLM API, Prompt Engineering, Tool Use

Groq'un ücretsiz LLM API'si üzerinden yapay zeka uygulamalarının temel yapı taşlarını öğrenme ve uygulama çalışması: API çağırma, çok turlu konuşma, prompt engineering teknikleri ve AI'ın kendi fonksiyonlarımızı çağırabilmesi (tool use).

## Kullanılan Teknolojiler

- Python
- Groq (ücretsiz, kredi kartı gerektirmeyen LLM API sağlayıcısı)
- python-dotenv (API anahtarının güvenli yönetimi)
- requests (dış API'lere istek atma — tool use içinde)
- pandas, SQLAlchemy (tool use örneğinde veri işleme ve PostgreSQL entegrasyonu)

## Proje Yapısı

```
ai-muhendisligi/
├── ilk_ai_cagrisi.py      # LLM API temeli: tek/çok turlu konuşma, system message
├── few_shot_ornek.py      # Few-shot prompting ile tutarlı format öğretme
├── structured_output.py   # AI'dan JSON formatında, işlenebilir cevap alma
├── tool_use_ornek.py      # AI'ın Python fonksiyonlarını çağırabilmesi (function calling)
├── .env                   # API anahtarı ve DB bilgileri (depoya dahil değildir)
└── README.md
```

## Kurulum

```
pip install groq python-dotenv requests pandas sqlalchemy psycopg2-binary
```

[console.groq.com](https://console.groq.com) üzerinden ücretsiz bir API anahtarı alıp `.env` dosyasına ekleyin:

```
GROQ_API_KEY=kendi-anahtariniz
```

`tool_use_ornek.py` PostgreSQL'e de yazdığı için, ayrıca veritabanı bağlantı bilgileri gerekir (bkz. `veri-analizi` reposundaki Phase 6.3):

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=veri_analizi_db
DB_USER=postgres
DB_PASSWORD=kendi-sifreniz
```

## Çalıştırma

```
python ilk_ai_cagrisi.py
python few_shot_ornek.py
python structured_output.py
python tool_use_ornek.py
```

## Ne Yapıyor?

### 1. LLM API Temeli (`ilk_ai_cagrisi.py`)
- `client.chat.completions.create()` ile bir LLM'e istek atma
- `messages` listesi ve `role`/`content` yapısı (`user`, `assistant`, `system`)
- Çok turlu konuşma: LLM'ler durumsuzdur (stateless) — "hafıza" hissi, önceki mesajların her istekte yeniden gönderilmesinden gelir
- `system` mesajı ile AI'ın üslubunu/rolünü yönlendirme (aynı soruya, farklı system mesajıyla tamamen farklı üslupta cevap alma karşılaştırması)

### 2. Prompt Engineering (`few_shot_ornek.py`, `structured_output.py`)
- **Few-shot prompting:** AI'a birkaç örnek `user`/`assistant` çifti göstererek istenen cevap formatını (örn. tek kelimelik duygu etiketi) öğretme — kural yazmak yerine örnekle gösterme
- **Structured output:** System mesajında kesin bir JSON formatı tarif edip, AI'ın çıktısını `json.loads()` ile gerçek bir Python nesnesine çevirme — böylece AI çıktısı doğrudan kod ile işlenebilir hale gelir

### 3. Tool Use / Function Calling (`tool_use_ornek.py`)
AI'ın, kullanıcının doğal dildeki isteğine göre kendi Python fonksiyonlarımızı çağırmasını sağlama.

**Akış:**
1. AI'a `tools` listesiyle hangi fonksiyonları çağırabileceği (isim, açıklama, parametre şeması) tanıtılır
2. Kullanıcı doğal dilde bir şey sorar (örn. "Ankara ve İzmir'in hava durumu nasıl?")
3. AI, cevap yerine bir `tool_calls` isteği döner: hangi fonksiyon, hangi parametrelerle çağrılmalı
4. Fonksiyon **gerçekten Python tarafında** çalıştırılır (AI kendi kendine çalıştırmaz, sadece talep eder)
5. Sonuç `role: "tool"` ile tekrar AI'a verilir
6. AI, ham veriyi kullanıcıya doğal bir cümleyle özetler

**Güvenlik mimarisi — okuma/yazma ayrımı:**

Bu projede AI'a yalnızca **okuma** (`hava_durumu_getir`) yetkisi verilmiştir. Veritabanına yazma (`veritabanina_kaydet`) fonksiyonu `tools` listesinde bulunmaz; sadece elle tetiklenen `pipeline_calistir()` içinde, geliştiricinin kontrolünde çağrılır. Bu tasarım kararının nedeni:

- **Geri alınabilirlik:** Okuma işlemlerinde hata olsa da hiçbir şey kalıcı olarak bozulmaz. Yazma işlemleri kalıcı iz bırakır ve geri almak zahmetlidir.
- **Yanlış yorumlama riski:** AI, doğal dili yorumlarken kullanıcının niyetini yanlış anlayabilir. Bu risk, yalnızca okuma işlemlerinde düşük; yazma işlemlerinde önemlidir.
- **En az yetki (least privilege) ilkesi:** Bir bileşene, işini yapması için gereken minimum yetki verilir — AI'ın hava durumunu söylemesi için veritabanına yazma yetkisine ihtiyacı yoktur.

`pipeline_calistir()` fonksiyonu hâlâ tam bir ETL akışı (extract → transform → load) çalıştırır, ancak bu akış **AI tarafından değil, geliştirici tarafından** tetiklenir.

## Öğrenilen Kavramlar

- LLM API'lere istek atma (`chat.completions.create`)
- `role`/`content` yapısı, çok turlu konuşma, LLM'lerin durumsuz (stateless) doğası
- System message ile davranış/üslup yönlendirme
- Few-shot prompting (örnekle format öğretme)
- Structured output ve `json.loads()` ile AI çıktısını işlenebilir veriye çevirme
- Tool use / function calling: `tools` şeması, `tool_calls`, `role: "tool"`
- AI'ın fonksiyon çağırma *isteğinde* bulunması ile fonksiyonun *gerçekten çalıştırılması* arasındaki fark
- Okuma/yazma yetkilerini ayırarak AI sistemlerinde risk azaltma (least privilege)
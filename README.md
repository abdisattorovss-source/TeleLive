# TeleLive

TeleLive — **Telegram API asosida ishlaydigan norasmiy messenjer** (Android).
U [Telegram for Android](https://github.com/DrKLO/Telegram) ochiq kodi asosida yig'iladi.
TeleLive Telegram ekotizimining bir qismi, lekin Telegram kompaniyasi tomonidan chiqarilmagan.

Litsenziya: GNU GPL v2 (yoki keyingi) — [LICENSE](LICENSE). Shu sababli bu repozitoriya **ochiq (public)** bo'lishi shart.

## 1-versiyada nima bor

| Imkoniyat | Holati |
|---|---|
| Nomi va logotipi TeleLive (Telegram belgisi olib tashlangan) | ✅ |
| 16 tagacha akkaunt (rasmiy Telegram'da 3–4 ta) | ✅ |
| O'zbekcha, ruscha, inglizcha | ✅ (uz/ru tarjimalari Telegram serveridan yuklanadi, TeleLive matnlari ilova ichida) |
| Kirish sahifasida "norasmiy ilova" yozuvi (Telegram talabi) | ✅ |
| Premium — @PremiumBot orqali (Google Play to'lovi o'chirilgan) | ✅ |
| O'zimizdan reklama yo'q | ✅ |
| Ixtiyoriy sharpacha rejimi | ⏳ keyingi versiya |
| SMS orqali kod so'rash tugmasi | ⏳ keyingi versiya |
| Kirish sahifasidagi animatsiyali logotipni almashtirish | ⏳ keyingi versiya |

## Papka tuzilishi

```
telelive.json              — asosiy sozlamalar: nom, paket, versiya, akkauntlar soni, ranglar
scripts/apply_telelive.py  — Telegram kodini TeleLive'ga aylantiruvchi skript
scripts/telelive_icons.py  — logotipni chizadi (belgini shu yerda o'zgartirasiz)
overlay/                   — TeleLive'ga xos Java kodi va uz/ru/en matnlar
branding/                  — tayyor logotiplar (Play Market uchun 512×512)
workflow/build.yml         — GitHub'da APK/AAB yig'ish (GitHub'da .github/workflows/ ichiga qo'yiladi)
```

Telegram'ning to'liq kodi (bir necha GB) bu yerda saqlanmaydi: GitHub uni har safar
`telelive.json` dagi aniq versiyada yuklab oladi va skript o'zgarishlarni qo'llaydi.

## Ishga tushirish — bosqichma-bosqich

### 1. API ID va API hash olish (majburiy)
1. Brauzerda **https://my.telegram.org** ga kiring, Telegram raqamingizni yozing. Kod Telegram'ga keladi.
2. **API development tools** bo'limini oching.
3. Formani to'ldiring: *App title* — `TeleLive`, *Short name* — `telelive`, *Platform* — `Android`.
4. **App api_id** (raqam) va **App api_hash** (32 belgi) chiqadi. Ularni hech kimga bermang.

### 2. GitHub repozitoriya
1. GitHub'da yangi **Public** repozitoriya oching, masalan `TeleLive`.
2. Shu papkadagi hamma fayllarni unga yuklang.
3. `workflow/build.yml` faylini GitHub'da **`.github/workflows/build.yml`** manziliga qo'ying (abdisattorovss-source/TeleLive repozitoriyasida bu allaqachon qilingan):
   repozitoriyada **Add file → Create new file**, nomiga `.github/workflows/build.yml` deb yozing va
   `workflow/build.yml` ichidagi matnni to'liq nusxalab joylang → **Commit changes**.

### 3. Secrets (maxfiy sozlamalar)
Repozitoriyada: **Settings → Secrets and variables → Actions → New repository secret**

| Nomi | Qiymati | Majburiymi |
|---|---|---|
| `TELEGRAM_API_ID` | 1-bosqichdagi api_id | ✅ |
| `TELEGRAM_API_HASH` | 1-bosqichdagi api_hash | ✅ |
| `GOOGLE_SERVICES_JSON` | Firebase'dagi `google-services.json` fayli ichidagi matn | push-bildirishnomalar uchun |
| `KEYSTORE_BASE64` | imzolash kaliti (base64) | Play Market uchun |
| `KEYSTORE_PASSWORD`, `KEY_ALIAS`, `KEY_PASSWORD` | kalit parollari | Play Market uchun |

**Firebase** (bildirishnomalar): console.firebase.google.com → yangi loyiha → Android ilova qo'shish →
paket nomi `uz.ferlo.telelive` → `google-services.json` faylini yuklab oling va ichidagi matnni secret'ga qo'ying.
Firebase'siz ham ilova ishlaydi, faqat ilova yopiq turganda xabar bildirishnomasi kelmaydi.

### 4. Yig'ish
1. Repozitoriyada **Actions** → **TeleLive yig'ish** → **Run workflow**.
2. Telefonda sinash uchun: `apk` + `arm64`. Play Market uchun: `aab`.
3. Birinchi yig'ish 1–2 soat davom etishi mumkin (Telegram'ning C++ qismlari ham kompilyatsiya qilinadi).
4. Tugagach, sahifaning pastidagi **Artifacts** bo'limidan faylni yuklab oling.

## Muhim qoidalar (Telegram API Terms of Service)

- Ilova nomida "Telegram" so'zi bo'lmasligi va Telegram logotipi ishlatilmasligi kerak.
- Play Market tavsifida ilova Telegram API'dan foydalanishi aniq yozilishi kerak (`store/` papkasidagi matnlarda bor).
- Kanallardagi Telegram'ning rasmiy homiylik xabarlari o'chirilmaydi.
- O'chirilgan xabarlarni saqlash, pulsiz Premium kabi funksiyalar qo'shilmaydi — ular qoidani buzadi.
- Qoida buzilsa, Telegram 10 kun muhlat beradi, keyin API'ni o'chiradi va ilovani do'kondan olib tashlatadi.

## Sozlamalarni o'zgartirish

`telelive.json` ni tahrirlang:
- `package` — paket nomi. **Play Market'ga birinchi marta yuklagandan keyin uni o'zgartirib bo'lmaydi.**
- `version_name` / `version_code` — har yangi Play versiyasida `version_code` ni 1 ga oshiring.
- `max_accounts` — akkauntlar soni.
- `icon_background` / `icon_foreground` — logotip ranglari.
- `telegram_commit` — Telegram kodining qaysi versiyasi olinishi.

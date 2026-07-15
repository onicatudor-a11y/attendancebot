# Bot de remindere zilnice — Telegram

Trimite automat, în fiecare dimineață, mai multe mesaje/sarcini în grup, la
ore diferite. În configurația implicită:

| Ora   | Ce trimite                                              | Tip     |
|-------|----------------------------------------------------------|---------|
| 08:00 | Cine e azi la lucru?                                     | sondaj  |
| 08:10 | Sarcină: răspuns la mesajele de pe AmoCRM                 | mesaj   |
| 08:20 | Sarcină: răspuns la mesaje și comentarii pe TikTok        | mesaj   |

Sondajul de prezență nu e anonim — se vede cine a răspuns ce.

## 1. Creezi botul (o singură dată)

1. În Telegram caută **@BotFather** → `/start` → `/newbot`.
2. Dă-i un nume (ex: "Prezență Echipă") și un username unic terminat în `bot`
   (ex: `PrezentaEchipaBot`).
3. Primești un **token** (ex: `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`) — păstrează-l secret.

## 2. Adaugi botul în grupul tău cu cei 4 oameni

Îl adaugi ca membru normal (nu are nevoie să fie admin).

## 3. Afli ID-ul grupului

În grup, scrie `/id` — botul va trebui să fie deja pornit (vezi pasul 4) ca
să răspundă. Îți dă un număr, de obicei negativ, ex: `-1001234567890`.
Acela e `GROUP_CHAT_ID`.

## 4. Pornești botul (găzduire)

Ai nevoie ca acest script să ruleze **tot timpul**, ca să trimită întrebarea
în fiecare dimineață. Cea mai simplă variantă, fără server propriu:

### Railway (recomandat, cel mai puțin efort)
1. Cont pe [railway.com](https://railway.com), conectezi GitHub.
2. Urci acest folder într-un repo nou pe GitHub.
3. Railway → **New Project → Deploy from GitHub repo**.
4. La **Variables**, adaugi:
   - `BOT_TOKEN` = tokenul de la BotFather
   - `GROUP_CHAT_ID` = ID-ul aflat la pasul 3 (dacă nu-l ai încă, pornește
     botul întâi fără el, scrie `/id` în grup, apoi adaugă valoarea)
   - `TIMEZONE` = ex `Europe/Chisinau` (implicit)
   - `DAYS` = zilele săptămânii, `0,1,2,3,4` pentru luni-vineri (implicit),
     sau `0,1,2,3,4,5,6` pentru toate zilele
5. Railway are un credit lunar mic gratuit; pentru rulare 24/7 constantă,
   planul Hobby (~$5/lună) e cea mai stabilă variantă.

### Testare locală rapidă
```bash
pip install -r requirements.txt
export BOT_TOKEN="tokenul_tau"
export GROUP_CHAT_ID="-1001234567890"
python3 bot.py
```

## Comenzi disponibile
- `/id` — arată ID-ul chatului curent (folosește-l o dată, ca să-l pui în configurare)
- `/acum` — arată lista de remindere și numărul fiecăruia
- `/acum 2` — trimite manual reminderul #2 chiar acum (util pt testare)

## Cum adaugi / modifici remindere

Toate remindere-le sunt în `config.py`, în lista `REMINDERS`. Fiecare intrare
arată așa:

```python
{
    "time": "08:10",
    "text": "📩 Sarcină: răspuns la mesajele de pe AmoCRM.",
    "poll": False,
},
```

Ca să adaugi unul nou, copiezi un bloc, îi schimbi ora și textul. Dacă vrei
să fie sondaj (ca oamenii să apese un răspuns), pui `"poll": True` și adaugi
`"options": ["Opțiune 1", "Opțiune 2"]`. După ce editezi `config.py`, faci
un nou deploy (push pe GitHub, dacă folosești Railway — se redeployează automat).

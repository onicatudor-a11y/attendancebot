import os

# Token de la @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# ID-ul grupului unde se trimite întrebarea zilnică.
# Îl afli scriind /id în grup, după ce adaugi botul.
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID", "")

# Fus orar, ex: "Europe/Chisinau"
TIMEZONE = os.getenv("TIMEZONE", "Europe/Chisinau")

# Zilele săptămânii în care se trimit remindere-le (0=luni ... 6=duminică).
# Implicit luni-vineri. Ex: "0,1,2,3,4,5,6" pentru toate zilele.
DAYS = os.getenv("DAYS", "0,1,2,3,4")

# ---------------------------------------------------------------------------
# Lista de remindere zilnice. Adaugă/șterge/modifică oricâte vrei aici.
#
# time    -> ora "HH:MM" la care se trimite
# text    -> textul mesajului
# poll    -> True = trimite ca sondaj (oamenii apasă un răspuns, vizibil pt toți)
#            False = trimite ca mesaj normal
# options -> doar dacă poll=True, listă de variante de răspuns
# ---------------------------------------------------------------------------
REMINDERS = [
    {
        "time": "08:00",
        "text": "☀️ Cine e azi la lucru?",
        "poll": True,
        "options": ["Sergiu", "Mihai"],
    },
    {
        "time": "08:10",
        "text": "📩 Sarcină: de răspuns la mesajele de pe AmoCRM, de schimbat la a 2 atingere seen mesajele de o zi în urmă.",
        "poll": False,
    },
    {
        "time": "08:30",
        "text": "🎵 Sarcină: de răspuns la mesaje și comentarii pe TikTok.",
        "poll": False,
    },
]

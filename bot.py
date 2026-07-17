import logging
import datetime
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Tine minte, in memorie, ce reminder a fost trimis azi (ca watchdog-ul sa nu il retrimita de mai multe ori)
_sent_today: dict[str, datetime.date] = {}


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Prinde orice eroare neasteptata (retea etc.) ca sa nu opreasca botul."""
    logger.error("A aparut o eroare neasteptata: %s", context.error, exc_info=context.error)


async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Helper command so you can find the group's chat_id to put in config."""
    await update.message.reply_text(f"ID-ul acestui chat este: {update.effective_chat.id}")


async def send_reminder(context: ContextTypes.DEFAULT_TYPE, chat_id: int, reminder: dict):
    if reminder.get("poll"):
        await context.bot.send_poll(
            chat_id=chat_id,
            question=reminder["text"],
            options=reminder["options"],
            is_anonymous=False,  # asa se vede cine a raspuns ce
            allows_multiple_answers=False,
        )
    else:
        await context.bot.send_message(chat_id=chat_id, text=reminder["text"])


async def scheduled_job(context: ContextTypes.DEFAULT_TYPE):
    reminder = context.job.data
    if not config.GROUP_CHAT_ID:
        logger.warning("GROUP_CHAT_ID nu este setat - nu pot trimite reminderul.")
        return
    await send_reminder(context, int(config.GROUP_CHAT_ID), reminder)
    _sent_today[reminder["text"]] = datetime.date.today()


async def watchdog_job(context: ContextTypes.DEFAULT_TYPE):
    """La fiecare 30 min, verifica daca vreun reminder de azi a fost ratat si il retrimite.

    Grace window: retrimite doar daca a trecut cu 10-240 minute peste ora programata,
    ca sa nu trimita reminder-e foarte vechi/nerelevante daca botul a stat oprit mult timp.
    """
    if not config.GROUP_CHAT_ID:
        return

    tz = ZoneInfo(config.TIMEZONE)
    now = datetime.datetime.now(tz)
    today = now.date()
    days = tuple(int(d) for d in config.DAYS.split(","))

    if now.weekday() not in days:
        return

    for reminder in config.REMINDERS:
        if _sent_today.get(reminder["text"]) == today:
            continue

        hour, minute = (int(x) for x in reminder["time"].split(":"))
        scheduled_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        delay = (now - scheduled_dt).total_seconds() / 60  # in minute

        if 10 <= delay <= 240:
            logger.warning(
                "Reminderul '%s' pare ratat (%.0f min intarziere) - il trimit acum.",
                reminder["text"], delay,
            )
            try:
                await send_reminder(context, int(config.GROUP_CHAT_ID), reminder)
                _sent_today[reminder["text"]] = today
            except Exception:
                logger.exception("Nu am putut retrimite reminderul ratat: %s", reminder["text"])


async def now_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trigger any reminder manually right now: /acum 1  (1 = primul din lista, etc.)"""
    if not context.args or not context.args[0].isdigit():
        names = "\n".join(
            f"{i + 1}. {r['text']} (ora {r['time']})" for i, r in enumerate(config.REMINDERS)
        )
        await update.message.reply_text(
            "Folosire: /acum <numar>\nRemindere disponibile:\n" + names
        )
        return
    idx = int(context.args[0]) - 1
    if idx < 0 or idx >= len(config.REMINDERS):
        await update.message.reply_text("Nu exista un reminder cu acest numar.")
        return
    await send_reminder(context, update.effective_chat.id, config.REMINDERS[idx])
    if int(update.effective_chat.id) == int(config.GROUP_CHAT_ID or 0):
        _sent_today[config.REMINDERS[idx]["text"]] = datetime.date.today()


def main():
    if not config.BOT_TOKEN:
        raise RuntimeError("Seteaza variabila de mediu BOT_TOKEN cu tokenul de la BotFather.")

    app = Application.builder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("acum", now_cmd))
    app.add_error_handler(error_handler)

    days = tuple(int(d) for d in config.DAYS.split(","))
    tz = ZoneInfo(config.TIMEZONE)

    # Watchdog: verifica la fiecare 30 min daca un reminder a fost ratat si il retrimite
    app.job_queue.run_repeating(watchdog_job, interval=1800, first=60)

    for reminder in config.REMINDERS:
        hour, minute = (int(x) for x in reminder["time"].split(":"))
        app.job_queue.run_daily(
            scheduled_job,
            time=datetime.time(hour=hour, minute=minute, tzinfo=tz),
            days=days,
            data=reminder,
            name=reminder["text"],
        )
        logger.info("Programat: '%s' la ora %s", reminder["text"], reminder["time"])

    logger.info("Bot pornit.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

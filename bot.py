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


def main():
    if not config.BOT_TOKEN:
        raise RuntimeError("Seteaza variabila de mediu BOT_TOKEN cu tokenul de la BotFather.")

    app = Application.builder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("acum", now_cmd))

    days = tuple(int(d) for d in config.DAYS.split(","))
    tz = ZoneInfo(config.TIMEZONE)

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

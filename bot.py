import os
import re
import gspread
from dotenv import load_dotenv
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

# ===== CONFIG =====
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SHEET_NAME = "UID Verification"

# ===== GOOGLE SHEETS SETUP =====
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)

client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# ===== BOT STATES =====
USERNAME, UID = range(2)


# ===== START COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Welcome to the Zana Trading Group verification.\n\n"
        "Please send your Telegram username.\n"
        "Example: @yourname"
    )

    return USERNAME


# ===== RECEIVE USERNAME =====
async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE):

    username = update.message.text.strip()

    if not username.startswith("@"):
        await update.message.reply_text(
            "Please send a valid Telegram username starting with @"
        )
        return USERNAME

    context.user_data["username"] = username

    await update.message.reply_text(
        "Now send your Bybit exchange UID.\n"

    )

    return UID


# ===== RECEIVE UID =====
async def receive_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.message.text.strip()

    # basic UID validation
    if not re.match(r"^\d{5,15}$", uid):
        await update.message.reply_text(
            "UID must be numbers only."
        )
        return UID

    tg_id = update.message.from_user.id
    username = context.user_data["username"]

    # check duplicates
    existing = sheet.col_values(3)

    if str(tg_id) in existing:
        await update.message.reply_text(
            "You have already submitted a UID."
        )
        return ConversationHandler.END

    # append row
    sheet.append_row(
        [
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            username,
            tg_id,
            uid,
        ]
    )

    await update.message.reply_text(
        "✅ UID submitted successfully.\n\n"
        "Admin will review your submission."
    )

    return ConversationHandler.END


# ===== CANCEL =====
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("Verification cancelled.")

    return ConversationHandler.END


# ===== MAIN =====
def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_username)
            ],
            UID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_uid)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()
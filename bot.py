import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Logging setup
logging.basicConfig(level=logging.INFO)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_user_info(update)

# /id command
async def get_id_by_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Provide a username. Example:\n`/id @username`", parse_mode="Markdown")
        return

    username = context.args[0].lstrip('@')
    try:
        user = await context.bot.get_chat(f"@{username}")
        name = user.full_name if hasattr(user, 'full_name') else user.title
        uid = user.id
        typ = "Bot" if getattr(user, 'is_bot', False) else "User"
        await update.message.reply_text(
            f"👤 {typ} Info:\n\n"
            f"🪪 Name: {name}\n"
            f"🆔 ID: `{uid}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Could not fetch ID. Reason:\n`{e}`", parse_mode="Markdown")

# Forwarded messages handler
async def forwarded(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    fwd = msg.forward_from or msg.forward_from_chat

    if not fwd:
        await msg.reply_text("❌ This doesn't seem to be a forwarded message.")
        return

    name = fwd.full_name if hasattr(fwd, 'full_name') else fwd.title
    uid = fwd.id
    is_bot = getattr(fwd, 'is_bot', False)
    typ = "Bot" if is_bot else ("User" if msg.forward_from else "Channel")

    await msg.reply_text(
        f"📦 Forwarded From:\n\n"
        f"📛 Name: {name}\n"
        f"🆔 ID: `{uid}`\n"
        f"🏷 Type: {typ}",
        parse_mode="Markdown"
    )

# Any message handler: show user info
async def any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_user_info(update)

# Reusable function to show user info
async def show_user_info(update: Update):
    user = update.effective_user
    msg = (
        f"👤 Your Info:\n\n"
        f"🪪 Name: {user.full_name}\n"
        f"💬 Username: @{user.username if user.username else 'N/A'}\n"
        f"🆔 User ID: `{user.id}`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# Run the bot
def run_bot():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN not set.")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id_by_username))
    app.add_handler(MessageHandler(filters.FORWARDED, forwarded))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, any_message))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()

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

# Enable logging
logging.basicConfig(level=logging.INFO)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = (
        f"👤 Your Info:\n\n"
        f"🪪 Name: {user.full_name}\n"
        f"💬 Username: @{user.username if user.username else 'N/A'}\n"
        f"🆔 User ID: `{user.id}`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# /id command with @username
async def get_id_by_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Please provide a username. Example:\n`/id @username`", parse_mode="Markdown")
        return

    username = context.args[0].lstrip('@')
    try:
        user = await context.bot.get_chat(f"@{username}")
        name = user.full_name
        uid = user.id
        typ = "Bot" if user.is_bot else "User"
        await update.message.reply_text(f"👤 {typ} Info:\n\n🪪 Name: {name}\n🆔 ID: `{uid}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Could not fetch ID. Reason:\n{e}")

# Handler for forwarded messages
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

# Main function
async def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN not set.")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id_by_username))
    app.add_handler(MessageHandler(filters.FORWARDED, forwarded))

    print("✅ Bot is running...")
    await app.run_polling()

# Entry point
if __name__ == "__main__":
    import asyncio

    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass

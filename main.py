from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import re

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Variabel global
tracked_users = {}


def start(update, context):
    """Handler untuk perintah /start."""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Halo! Saya akan melacak perubahan nama dan username Anda. "
                                                                    "Tambahkan saya ke grup dan berikan hak admin untuk memulai pelacakan.")


def track(update, context):
    """Handler untuk melacak perubahan nama dan username."""
    user = update.effective_user

    if user.id in tracked_users:
        tracked_users[user.id]['name'] = user.full_name
        tracked_users[user.id]['username'] = user.username
    else:
        tracked_users[user.id] = {
            'name': user.full_name,
            'username': user.username
        }

    context.bot.send_message(chat_id=update.effective_chat.id, text="Anda telah ditambahkan ke daftar pelacakan.")


def new_chat_member(update, context):
    """Handler untuk anggota chat baru."""
    user = update.message.new_chat_members[0]

    if user.id in tracked_users and user.full_name != tracked_users[user.id]['name']:
        text = f"🔔 Peringatan Perubahan Nama! 🔔\n\n"
        text += f"User: {user.full_name} ({user.id})\n"
        text += f"Nama Lama: {tracked_users[user.id]['name']}\n"
        text += f"Nama Baru: {user.full_name}"

        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        tracked_users[user.id]['name'] = user.full_name


def username_change(update, context):
    """Handler untuk perubahan username."""
    user = update.effective_user

    if user.id in tracked_users and user.username != tracked_users[user.id]['username']:
        text = f"🔔 Peringatan Perubahan Username! 🔔\n\n"
        text += f"User: {user.full_name} ({user.id})\n"
        text += f"Username Lama: {tracked_users[user.id]['username']}\n"
        text += f"Username Baru: {user.username}"

        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        tracked_users[user.id]['username'] = user.username


def echo_all(update, context):
    """Handler untuk tipe pesan lainnya."""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Maaf, saya hanya melacak perubahan nama dan username.")


def error_handler(update, context):
    """Handler untuk error."""
    logger.warning(f"Update {update} menyebabkan error.")


def main():
    """Fungsi utama untuk menjalankan bot."""
    # Membuat Updater dengan token bot Anda
    updater = Updater("TOKEN_ANDA", use_context=True)

    # Mendapatkan dispatcher untuk mendaftarkan handler
    dispatcher = updater.dispatcher

    # Mendaftarkan handler
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("track", track))
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_chat_member))
    dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'.+?(?<!\w)@[A-Za-z0-9_]+(?!\w)'), re.IGNORECASE), username_change))
    dispatcher.add_handler(MessageHandler(Filters.all, echo_all))

    # Log errors
    dispatcher.add_error_handler(error_handler)

    # Memulai bot
    updater.start_polling()

    # Menjalankan bot sampai Ctrl+C ditekan
    updater.idle()


if __name__ == '__main__':
    main()

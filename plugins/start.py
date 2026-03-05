from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, URLInputFile
from config import CHANNEL_URL, DEV_URL, LOG_CHANNEL
from database import add_user, is_banned, get_user
import time

router = Router()

def small_caps(text: str) -> str:
    """Convert text to small caps unicode."""
    normal = "abcdefghijklmnopqrstuvwxyz"
    small = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    result = ""
    for char in text:
        if char.lower() in normal:
            idx = normal.index(char.lower())
            result += small[idx]
        else:
            result += char
    return result

@router.message(Command("start"))
async def start_cmd(message: types.Message, bot: Bot):
    """Handle /start command with specific image and buttons."""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    # Check if banned
    if await is_banned(user_id):
        await message.answer(small_caps("You are banned from using this bot."))
        return

    # Check if new user
    existing_user = await get_user(user_id)
    is_new_user = existing_user is None

    # Add/update user in database
    await add_user(user_id, username, first_name)

    # Log new user to log channel
    if is_new_user and LOG_CHANNEL:
        try:
            await bot.send_message(
                chat_id=LOG_CHANNEL,
                text=f"👤 <b>ɴᴇᴡ ᴜsᴇʀ</b>\n\n"
                     f"🆔 <code>{user_id}</code>\n"
                     f"👤 {first_name}\n"
                     f"🔗 @{username or 'N/A'}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    # Welcome text in small caps with blockquote
    welcome_text = (
        f"<b>{small_caps('Welcome to Msmaxpro Thumbnail Bot!')}</b>\n\n"
        f"<blockquote>{small_caps('I am the fastest bot to add custom thumbnails to your videos instantly.')}</blockquote>\n\n"
        f"<b>{small_caps('How to use:')}</b>\n"
        f"<blockquote>"
        f"1️ {small_caps('Set your thumbnail in Settings')}\n"
        f"2️ {small_caps('Send any video file')}\n"
        f"3️ {small_caps('Receive your processed video!')}"
        f"</blockquote>"
    )

    # Buttons (Elite White Style Emojis)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚪ Join Channel", url=CHANNEL_URL),
            InlineKeyboardButton(text="⚪ Developer", url=DEV_URL)
        ],
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
    ])

    # Direct image link provided by user
    IMAGE_URL = "https://files.catbox.moe/yx82fq.jpg"

    try:
        # Sending the specific photo with caption
        photo = URLInputFile(IMAGE_URL)
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption=welcome_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        # Fallback if image fails (Optional logging of error)
        print(f"Error sending start photo: {e}")
        await message.answer(
            welcome_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

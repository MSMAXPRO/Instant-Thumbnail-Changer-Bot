import psutil
import time
from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_URL, DEV_URL, LOG_CHANNEL
from database import add_user, is_banned, get_user

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
    # --- 1. Latency & Metrics Logic ---
    start_time = time.perf_counter()
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    # Check Ban Status
    if await is_banned(user_id):
        await message.answer(small_caps("You are banned from using this bot."))
        return

    # User Database Logic
    existing_user = await get_user(user_id)
    is_new_user = existing_user is None
    await add_user(user_id, username, first_name)

    # Dynamic Metrics Calculation
    cpu_load = psutil.cpu_percent()
    # Latency estimation based on processing time
    end_time = time.perf_counter()
    latency = round((end_time - start_time) * 1000, 2)

    # Log New User
    if is_new_user and LOG_CHANNEL:
        try:
            await bot.send_message(
                chat_id=LOG_CHANNEL,
                text=f"👤 <b>ɴᴇᴡ ᴜsᴇʀ</b>\n\n🆔 <code>{user_id}</code>\n👤 {first_name}\n🔗 @{username or 'N/A'}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    # --- 2. Hybrid UI Text Construction ---
    hybrid_text = (
        f"🖥️ <b>{small_caps('MSMAXPRO THUMBNAIL ENGINE v2.0')}</b>\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
        f"📊 <b>{small_caps('Session Metrics:')}</b>\n"
        f"┣ ⚡ {small_caps('Status:')} <b>Online & Fast</b>\n"
        f"┣ 🟢 {small_caps('Server Load:')} <b>{cpu_load}%</b>\n"
        f"┗ 📶 {small_caps('Latency:')} <b>{latency}ms</b>\n\n"
        f"👤 <b>{small_caps('Operator:')}</b> <code>{first_name}</code>\n"
        f"┣ 🔑 {small_caps('Access:')} <b>PREMIUM</b>\n"
        f"┗ 📅 {small_caps('Active Plan:')} <b>Lifetime</b>\n\n"
        f"📖 <b>{small_caps('How to use:')}</b>\n"
        f"1️⃣ {small_caps('Go to /settings to set your')} 🖼️\n"
        f"2️⃣ {small_caps('Send any')} 🎬 {small_caps('Video file')}\n"
        f"3️⃣ {small_caps('Receive your processed video!')}\n\n"
        f"🛠️ <b>{small_caps('Available Commands:')}</b>\n"
        f"• /start - {small_caps('Restart Interface')}\n"
        f"• /settings - {small_caps('Change Thumbnail')}\n"
        f"• /plan - {small_caps('Upgrade Access')}\n\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"👇 <b>{small_caps('Choose an option below:')}</b>"
    )

    # --- 3. Hybrid Buttons (Image 1 Style) ---
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚪ Join Channel", url=CHANNEL_URL),
            InlineKeyboardButton(text="⚪ Developer", url=DEV_URL)
        ],
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
    ])

    # --- 4. Sending Photo with Hybrid Text ---
    IMAGE_URL = "https://files.catbox.moe/yx82fq.jpg"

    try:
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=IMAGE_URL,
            caption=hybrid_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Photo sending failed: {e}")
        await message.answer(
            hybrid_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

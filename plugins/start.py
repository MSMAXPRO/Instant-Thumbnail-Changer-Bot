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
    # --- 1. System Metrics & Latency ---
    start_time = time.perf_counter()
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    # Check Ban Status
    if await is_banned(user_id):
        await message.answer(small_caps("You are banned from using this bot."))
        return

    # Database Logic (User add/fetch)
    await add_user(user_id, username, first_name)
    user_data = await get_user(user_id)

    # Dynamic Metrics Calculation
    try:
        cpu_load = psutil.cpu_percent()
    except:
        cpu_load = "N/A"
    
    end_time = time.perf_counter()
    latency = round((end_time - start_time) * 1000, 2)

    # Log New User (Agar naya hai toh)
    # Note: is_new_user logic yahan database pe depend karega
    if LOG_CHANNEL:
        try:
            # Short Log logic
            pass 
        except Exception:
            pass

    # --- 2. User Status Logic (Ghost OS Style) ---
    # Database se status uthao (is_premium, expiry, used_count)
    is_premium = user_data.get("is_premium", False) if user_data else False
    expiry = user_data.get("expiry_date", "N/A") if user_data else "N/A"
    used = user_data.get("videos_used", 0) if user_data else 0

    if is_premium:
        access_level = "PREMIUM 👑"
        limit_val = "Unlimited ♾️"
        expiry_val = expiry
    else:
        access_level = "FREE USER"
        limit_val = f"{used}/40 📊"
        expiry_val = "N/A"

    # --- 3. Hybrid UI Text Construction ---
    hybrid_text = (
        f"🖥️ <b>{small_caps('MSMAXPRO THUMBNAIL ENGINE v2.0')}</b>\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
        f"📊 <b>{small_caps('System Metrics:')}</b>\n"
        f"┣ ⚡ {small_caps('Status:')} <b>Online & Fast</b>\n"
        f"┣ 🟢 {small_caps('Server Load:')} <b>{cpu_load}%</b>\n"
        f"┗ 📶 {small_caps('Latency:')} <b>{latency}ms</b>\n\n"
        f"👤 <b>{small_caps('Operator Details:')}</b>\n"
        f"┣ 🆔 {small_caps('Identity:')} <code>{first_name}</code>\n"
        f"┣ 🔑 {small_caps('Access Level:')} <b>{access_level}</b>\n"
        f"┣ ⏳ {small_caps('Expires In:')} <b>{expiry_val}</b>\n"
        f"┗ 🎬 {small_caps('Daily Limit:')} <b>{limit_val}</b>\n\n"
        f"📖 <b>{small_caps('How to use:')}</b>\n"
        f"1️⃣ {small_caps('Set your thumbnail in /settings')} 🖼️\n"
        f"2️⃣ {small_caps('Send any')} 🎬 {small_caps('Video file')}\n"
        f"3️⃣ {small_caps('Receive your processed video!')}\n\n"
        f"🛠️ <b>{small_caps('Available Modules:')}</b>\n"
        f"• /start - {small_caps('Restart Interface')}\n"
        f"• /settings - {small_caps('Thumbnail Config')}\n"
        f"• /plan - {small_caps('Upgrade Access')} 💎\n\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"👇 <b>{small_caps('Choose an option below:')}</b>"
    )

    # --- 4. Hybrid Buttons (Image 1 Style) ---
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚪ Join Channel", url=CHANNEL_URL),
            InlineKeyboardButton(text="⚪ Developer", url=DEV_URL)
        ],
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
    ])

    # Direct URL for reliability
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
        # Fallback to text if photo fails
        await message.answer(
            hybrid_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

from aiogram import Router, types, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import LOG_CHANNEL
from database import get_thumbnail, increment_usage, is_banned, add_user

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

@router.message(F.video)
async def handle_video(message: types.Message, bot: Bot):
    """Handle incoming video and send it back with user's thumbnail as cover."""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Check if banned
    if await is_banned(user_id):
        await message.answer(small_caps("You are banned from using this bot."))
        return
    
    # Add/update user
    await add_user(user_id, username, first_name)
    # --- START: NEW PREMIUM/FREE LIMIT LOGIC ---
    user_data = await get_user(user_id) # Fetch latest data
    is_premium = user_data.get("is_premium", False) if user_data else False
    used_count = user_data.get("videos_used", 0) if user_data else 0

    if not is_premium and used_count >= 40:
        limit_text = (
            f"⚠️ <b>{small_caps('Daily Limit Reached!')}</b>\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
            f"👤 <b>{small_caps('Operator:')}</b> <code>{first_name}</code>\n"
            f"📊 <b>{small_caps('Usage:')}</b> <code>{used_count}/40</code>\n\n"
            f"<blockquote>{small_caps('Your free limit is over. Upgrade to Premium for unlimited access.')}</blockquote>"
        )
        # Inline button for /plan command
        plan_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 View Premium Plans", callback_data="view_plans")],
            [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
        ])
        await message.answer(limit_text, parse_mode="HTML", reply_markup=plan_keyboard)
        return # Processing stop kar dega
    # --- END: NEW PREMIUM/FREE LIMIT LOGIC ---
    video = message.video
    
    # Keep ORIGINAL caption - no modification
    caption = message.caption or ""
    
    # Get user's thumbnail
    thumb_file_id = await get_thumbnail(user_id)
    
    # Build keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
    ])
    
    if thumb_file_id:
        # Increment usage count
        await increment_usage(user_id)
        
        # Send video with custom cover
        await bot.send_video(
            chat_id=message.chat.id,
            video=video.file_id,
            caption=caption,
            cover=thumb_file_id,
            reply_markup=keyboard
        )
        
        # Log video to log channel
        if LOG_CHANNEL:
            try:
                await bot.send_message(
                    chat_id=LOG_CHANNEL,
                    text=f"📹 <b>ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇssᴇᴅ</b>\n\n"
                         f"🆔 <code>{user_id}</code>\n"
                         f"👤 {first_name} (@{username or 'N/A'})\n"
                         f"📝 {caption[:50] + '...' if len(caption) > 50 else caption or 'No caption'}",
                    parse_mode="HTML"
                )
            except Exception:
                pass
    else:
        # No thumbnail set - send warning
        await message.answer(
            f"<b>⚠️ {small_caps('No thumbnail set!')}</b>\n\n"
            f"<blockquote>{small_caps('Please set a thumbnail first using Settings.')}</blockquote>",
            parse_mode="HTML",
            reply_markup=keyboard
        )

# CantarellaBots | Updated by MSMAXPRO
from aiogram import Router, types, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import LOG_CHANNEL
from database import get_thumbnail, increment_usage, is_banned, add_user, get_user

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
    """Handle incoming video with Premium/Free limit logic."""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # 1. Check if banned
    if await is_banned(user_id):
        await message.answer(small_caps("You are banned from using this bot."))
        return
    
    # 2. Add/Fetch User Data
    await add_user(user_id, username, first_name)
    user_data = await get_user(user_id)
    
    # 3. Premium & Limit Logic (The "Ghost OS" way)
    is_premium = user_data.get("is_premium", False) if user_data else False
    used_count = user_data.get("videos_used", 0) if user_data else 0
    
    # Keyboard for responses
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
    ])

    # Check Limit for Free Users
    if not is_premium and used_count >= 40:
        limit_reached_text = (
            f"⚠️ <b>{small_caps('Daily Limit Reached!')}</b>\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
            f"👤 <b>{small_caps('Operator:')}</b> <code>{first_name}</code>\n"
            f"📊 <b>{small_caps('Usage:')}</b> <code>{used_count}/40</code>\n\n"
            f"<blockquote>{small_caps('Your free daily limit is over. Upgrade to Premium for unlimited processing!')}</blockquote>\n\n"
            f"💎 {small_caps('Use /plan to see premium offers.')}"
        )
        await message.answer(limit_reached_text, parse_mode="HTML", reply_markup=keyboard)
        return

    # 4. Processing Video
    video = message.video
    caption = message.caption or ""
    thumb_file_id = await get_thumbnail(user_id)
    
    if thumb_file_id:
        # Increment usage in database
        await increment_usage(user_id)
        
        # UI Feedback (Optional: "Processing..." message delete kar sakte ho)
        status_msg = await message.answer(f"⚡ <b>{small_caps('Injecting Thumbnail...')}</b>", parse_mode="HTML")

        try:
            # Send video with custom cover
            await bot.send_video(
                chat_id=message.chat.id,
                video=video.file_id,
                caption=caption,
                thumbnail=thumb_file_id, # aiogram v3 uses 'thumbnail' instead of 'cover'
                reply_markup=keyboard
            )
            await status_msg.delete()
        except Exception as e:
            await status_msg.edit_text(f"❌ <b>{small_caps('Error during processing')}</b>", parse_mode="HTML")
            print(f"Error: {e}")
            return
        
        # Log to log channel
        if LOG_CHANNEL:
            try:
                acc_type = "💎 ᴘʀᴇᴍɪᴜᴍ" if is_premium else "🆓 ғʀᴇᴇ"
                await bot.send_message(
                    chat_id=LOG_CHANNEL,
                    text=f"📹 <b>ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇssᴇᴅ</b>\n"
                         f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                         f"👤 ᴜsᴇʀ: {first_name} (@{username or 'N/A'})\n"
                         f"🆔 ɪᴅ: <code>{user_id}</code>\n"
                         f"🔑 ᴛʏᴘᴇ: {acc_type}\n"
                         f"📝 ᴄᴀᴘᴛɪᴏɴ: {caption[:30] + '...' if len(caption) > 30 else caption or 'None'}",
                    parse_mode="HTML"
                )
            except Exception:
                pass
    else:
        # No thumbnail set
        await message.answer(
            f"<b>⚠️ {small_caps('No thumbnail set!')}</b>\n\n"
            f"<blockquote>{small_caps('Please set a thumbnail first in settings to process videos.')}</blockquote>",
            parse_mode="HTML",
            reply_markup=keyboard
        )

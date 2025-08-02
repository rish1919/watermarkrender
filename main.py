import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.watermark import add_watermark_image, add_watermark_video
from utils.claims import is_authorized, generate_code, claim_code
from utils.storage import get_watermark_path

logging.basicConfig(level=logging.INFO)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = Client("watermark_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start(_, msg: Message):
    await msg.reply("👋 Welcome to the Watermark Bot!\nUse /claimcode to get access.")

@bot.on_message(filters.command("claimcode"))
async def claim(_, msg: Message):
    if msg.from_user.id == OWNER_ID:
        code = generate_code()
        await msg.reply(f"🔐 Claim Code: `{code}`")
    else:
        code = msg.text.split(" ", 1)[-1].strip()
        success = claim_code(msg.from_user.id, code)
        if success:
            await msg.reply("✅ Access granted!")
        else:
            await msg.reply("❌ Invalid or used code.")

@bot.on_message(filters.command("setwm") & filters.user(OWNER_ID) & filters.reply)
async def set_wm(_, msg: Message):
    if msg.reply_to_message.photo or msg.reply_to_message.document:
        file = await msg.reply_to_message.download()
        os.makedirs("watermarks", exist_ok=True)
        os.rename(file, get_watermark_path())
        await msg.reply("✅ Watermark updated!")
    else:
        await msg.reply("❌ Please reply to a PNG image.")

@bot.on_message(filters.command("showwm") & filters.user(OWNER_ID))
async def show_wm(_, msg: Message):
    if os.path.exists(get_watermark_path()):
        await msg.reply_photo(get_watermark_path())
    else:
        await msg.reply("❌ No watermark set.")

@bot.on_message(filters.command("dltwm") & filters.user(OWNER_ID))
async def del_wm(_, msg: Message):
    if os.path.exists(get_watermark_path()):
        os.remove(get_watermark_path())
        await msg.reply("✅ Watermark removed.")
    else:
        await msg.reply("⚠️ No watermark found.")

@bot.on_message(filters.channel & (filters.video | filters.photo | filters.document))
async def auto_watermark(_, msg: Message):
    if not is_authorized(msg.from_user.id if msg.from_user else 0):
        return

    wm_path = get_watermark_path()
    if not os.path.exists(wm_path):
        return

    if msg.photo or (msg.document and msg.document.mime_type.startswith("image")):
        file_path = await msg.download()
        result = add_watermark_image(file_path, wm_path)
        if result:
            await msg.reply_photo(result, caption=msg.caption or "")
            os.remove(result)
    elif msg.video or (msg.document and msg.document.mime_type.startswith("video")):
        file_path = await msg.download()
        result = add_watermark_video(file_path, wm_path)
        if result:
            await msg.reply_video(result, caption=msg.caption or "")
            os.remove(result)

bot.run()
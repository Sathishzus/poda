from pyrogram import filters

from wbb import app
from wbb.core.decorators.errors import capture_err
from wbb.utils.http import get

__MODULE__ = "Repo"
__HELP__ = (
    "/repo - To Get My Github Repository Link "
    "And Support Group Link"
)


@app.on_message(filters.command("gban") & ~filters.edited)
@capture_err
async def repo(_, message):
    text = f"""Joker Gban(Global Banning) system is temporarily unavailable. Untill further notice."""
    await app.send_message(
        message.chat.id, text=text, disable_web_page_preview=True
    )
from pyrogram import filters

from prime import app
from prime.core.decorators.errors import capture_err
from prime.utils.http import get

__MODULE__ = "Repo"
__HELP__ = (
    "/repo - To Get My Github Repository Link "
    "And Support Group Link"
)


@app.on_message(filters.command("iloveyou") & ~filters.edited)
@capture_err
async def repo(_, message):
    text = f"""Kari kolambula ealumbu un kathaiea vaeanam kealambu"""
    await app.send_message(
        message.chat.id, text=text, disable_web_page_preview=True
    )

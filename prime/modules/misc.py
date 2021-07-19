import secrets
import string

import aiohttp
from cryptography.fernet import Fernet
from pyrogram import filters

from prime import FERNET_ENCRYPTION_KEY, app, arq
from prime.core.decorators.errors import capture_err
from prime.utils import random_line
from prime.utils.http import get
from prime.utils.json_prettify import json_prettify
from prime.utils.pastebin import paste


# Encrypt
@app.on_message(filters.command("encrypt") & ~filters.edited)
@capture_err
async def encrypt(_, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "Reply To A Message To Encrypt It."
        )
    text = message.reply_to_message.text
    text_in_bytes = bytes(text, "utf-8")
    cipher_suite = Fernet(FERNET_ENCRYPTION_KEY)
    encrypted_text = cipher_suite.encrypt(text_in_bytes)
    bytes_in_text = encrypted_text.decode("utf-8")
    await message.reply_text(bytes_in_text)


# Decrypt
@app.on_message(filters.command("decrypt") & ~filters.edited)
@capture_err
async def decrypt(_, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "Reply To A Message To Decrypt It."
        )
    text = message.reply_to_message.text
    text_in_bytes = bytes(text, "utf-8")
    cipher_suite = Fernet(FERNET_ENCRYPTION_KEY)
    try:
        decoded_text = cipher_suite.decrypt(text_in_bytes)
    except Exception:
        return await message.reply_text("Incorrect token")
    bytes_in_text = decoded_text.decode("utf-8")
    await message.reply_text(bytes_in_text)


async def fetch_text(url):
    async with aiohttp.ClientSession(
        headers={"user-agent": "curl"}
    ) as session:
        async with session.get(url) as resp:
            data = await resp.text()
    return data


# Translate
@app.on_message(filters.command("tr") & ~filters.edited)
@capture_err
async def tr(_, message):
    if len(message.command) != 2:
        return await message.reply_text("/tr [LANGUAGE_CODE]")
    lang = message.text.split(None, 1)[1]
    if not message.reply_to_message or not lang:
        return await message.reply_text(
            "Reply to a message with /tr [language code]"
            + "\nGet supported language list from here -"
            + " https://py-googletrans.readthedocs.io/en"
            + "/latest/#googletrans-languages"
        )
    reply = message.reply_to_message
    text = reply.text or reply.caption
    if not text:
        return await message.reply_text(
            "Reply to a text to translate it"
        )
    result = await arq.translate(text, lang)
    if not result.ok:
        return await message.reply_text(result.result)
    await message.reply_text(result.result.translatedText)


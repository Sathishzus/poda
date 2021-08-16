import os

from pyrogram import filters
from pyrogram.types import Message

from prime import SUDOERS, app ,BOT_ID, BOT_NAME
from prime.core.decorators.errors import capture_err
from prime.modules.trust import get_spam_probability
from prime.utils.dbfunctions import is_gbanned_user, user_global_karma

__MODULE__ = "Info"
__HELP__ = """
/info [USERNAME|ID] - Get info about a user.
/chat_info [USERNAME|ID] - Get info about a chat.
"""


async def get_user_info(user):
    user = await app.get_users(user)
    if not user.first_name:
        return ["Deleted account", None]
    user_id = user.id
    username = user.username
    first_name = user.first_name
    mention = user.mention("Link")
    dc_id = user.dc_id
    photo_id = None
    is_gbanned = await is_gbanned_user(user_id)
    is_sudo = user_id in SUDOERS
    status = user.status
    karma = await user_global_karma(user_id)
    spam_probab, n_messages = await get_spam_probability(user_id)
    isSpammer = (
        True
        if spam_probab > 50
        else False
        if spam_probab != 0
        else "Uncertain"
    )
    spam_probab = (
        str(round(spam_probab)) + " %"
        if spam_probab != 0
        else "Uncertain"
    )
    caption = f"""
🧍‍♂️ **Name:** {first_name}
🤵 **Username:** {("@" + username) if username else None}
🎴 **ID:** `{user_id}`
🌐 **DC:** {dc_id}
🔗 **Permalink:** {mention}
🚔 **Sudo:** {is_sudo}
👍 **Karma:** {karma}
📡 **Gbanned:** {is_gbanned}
📶 **Status:** {status}

🃏 **{BOT_NAME} Spam Detection** 🃏
🚷 **Spammer:** {isSpammer}
💯 **Spam Probability:** {spam_probab}
❓ __Stats Of Last {n_messages} Messages.__
"""
    return [caption, photo_id]


async def get_chat_info(chat):
    chat = await app.get_chat(chat)
    chat_id = chat.id
    username = chat.username
    title = chat.title
    type = chat.type
    is_scam = chat.is_scam
    description = chat.description
    members = chat.members_count
    is_restricted = chat.is_restricted
    link = f"[Link](t.me/{username})" if username else None
    dc_id = chat.dc_id
    photo_id = None
    caption = f"""
🎴 **ID:** `{chat_id}`
🌐 **DC:** {dc_id}
⚙️ **Type:** {type}
🧍‍♂️  **Name:** {title}
🤵 **Username:** {("@" + username) if username else None}
🔗 **Permalink:** {link}
👨‍👩‍👧‍👦**Members:** {members}
🔇 **Scam:** {is_scam}
🔕 **Restricted:** {is_restricted}
💭 **Description:** {description}
"""
    return [caption, photo_id]


@app.on_message(filters.command("info"))
@capture_err
async def info_func(_, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user.id
    elif not message.reply_to_message and len(message.command) == 1:
        user = message.from_user.id
    elif not message.reply_to_message and len(message.command) != 1:
        user = message.text.split(None, 1)[1]
    m = await message.reply_text("Processing")
    try:
        info_caption, photo_id = await get_user_info(user)
    except Exception as e:
        return await m.edit(str(e))
    if not photo_id:
        return await m.edit(
            info_caption, disable_web_page_preview=True
        )
    photo = await app.download_media(photo_id)
    await message.reply_photo(
        photo, caption=info_caption, quote=False
    )
    await m.delete()
    os.remove(photo)


@app.on_message(filters.command("chatinfo"))
@capture_err
async def chat_info_func(_, message: Message):
    try:
        if len(message.command) > 2:
            return await message.reply_text(
                "**Usage:**/chat_info [USERNAME|ID]"
            )
        elif len(message.command) == 1:
            chat = message.chat.id
        elif len(message.command) == 2:
            chat = message.text.split(None, 1)[1]
        m = await message.reply_text("Processing")
        info_caption, photo_id = await get_chat_info(chat)
        if not photo_id:
            return await m.edit(
                info_caption, disable_web_page_preview=True
            )
        photo = await app.download_media(photo_id)
        await message.reply_photo(
            photo, caption=info_caption, quote=False
        )
        await m.delete()
        os.remove(photo)
    except Exception as e:
        await message.reply_text(e)
        print(e)
        await m.delete()

from pyrogram import filters
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)

from prime import LOG_GROUP_ID, SUDOERS, USERBOT_PREFIX, app, app2, arq
from prime.core.decorators.permissions import adminsOnly
from prime.modules.admin import list_admins, member_permissions
from prime.modules.trust import get_spam_data
from prime.modules.userbot import edit_or_reply
from prime.utils.dbfunctions import (is_spam_detection_on,
                                   spam_detection_off,
                                   spam_detection_on)
from prime.utils.filter_groups import spam_protection_group

__MODULE__ = "AntiSpam"

@app.on_message(
    (filters.text | filters.caption) & ~filters.private & ~filters.me,
    group=spam_protection_group,
)
async def spam_protection_func(_, message: Message):
    text = message.text or message.caption
    chat_id = message.chat.id
    user = message.from_user
    if not text or not user:
        return

    # We'll handle admins only if it's spam, ignore only sudo users for now.
    if user.id in SUDOERS:
        return
    enabled = await is_spam_detection_on(chat_id)
    if not enabled:
        return
    data = await get_spam_data(message, text)
    if isinstance(data, str):
        return
    if not data.is_spam:
        return
    if user.id in (await list_admins(chat_id)):
        return
    


dev_forward = (
    "If you're not a developer of 🦊 𝔽𝕠𝕩 𝕏 𝔹𝕠𝕥, forward this message to devs, "
    + "so that they can use it to improve spam protection algorithm."
)


@app.on_callback_query(filters.regex("s_p_"))
async def spam_p_callback(_, cq: CallbackQuery):
    from_user = cq.from_user
    chat_id = cq.message.chat.id

    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_delete_messages"
    if permission not in permissions:
        return await cq.answer(
            "You don't have enough permissions to perform this action.\n"
            + f"Permission needed: {permission}",
            show_alert=True,
        )

    if cq.data.split("_")[-1] == "spam":
        try:
            await cq.message.reply_to_message.delete()
        except Exception:
            await cq.message.delete()
            return
        text = cq.message.text.markdown
        text = text.replace(
            "Alerted",
            f"Deleted Message With {from_user.mention}'s Approval.",
        )
        await cq.message.edit(text)
        if cq.message.reply_to_message:
            text = f"**ADMINS OF {chat_id} FLAGGED THIS MESSAGE AS SPAM**\n\n"
            text += f"`{cq.message.reply_to_message.text.markdown}`\n\n__{dev_forward}__"
            return await app.send_message(
                LOG_GROUP_ID, text, disable_web_page_preview=True
            )
        return

    await cq.message.delete()
    if cq.message.reply_to_message:
        text = f"**ADMINS OF {chat_id} FLAGGED THIS MESSAGE AS NOT SPAM**\n\n"
        text += f"`{cq.message.reply_to_message.text.markdown}`\n\n__{dev_forward}__"
        return await app.send_message(
            LOG_GROUP_ID, text, disable_web_page_preview=True
        )


@app.on_message(filters.command("addprofanity") & ~filters.private)
async def spam_flag_func(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text(
            "Reply to a message to flag it as __**#PROFANIT**__"
        )

    r = message.reply_to_message
    if not r.text and not r.caption:
        return await message.reply_text(
            "Reply to a text message to flag it as __**#PROFANITY**__"
        )

    text = r.text or r.caption
    if not text:
        return await message.reply_text(
            "Reply to a text message to flag it as __**#PROFANITY**__"
        )

    msg = f"""
**ADMINS OF {message.chat.id} FLAGGED THIS MESSAGE AS __**#PROFANITY**__. [Suggestion]**

{text.markdown}

__{dev_forward}__
"""
    await message.reply_text(
        "Message was flagged as __**#PROFANITY**__, Devs will use it to improve __**#PROFANITY**__ protection algorithm."
    )
    await app.send_message(
        LOG_GROUP_ID, msg, disable_web_page_preview=True
    )


@app.on_message(filters.command("spam_detection") & ~filters.private)
@adminsOnly("can_change_info")
async def spam_toggle(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "Usage: /spam_detection [ENABLE|DISABLE]"
        )
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status == "enable":
        await spam_detection_on(chat_id)
        await message.reply_text("Enabled Spam Detection System.")
    elif status == "disable":
        await spam_detection_off(chat_id)
        await message.reply_text("Disabled Spam Detection System.")
    else:
        await message.reply_text(
            "Unknown Suffix, Use /spam_detection [ENABLE|DISABLE]"
        )


@app.on_message(filters.command("spamscan"))
@app2.on_message(
    filters.command("spamscan", prefixes=USERBOT_PREFIX)
    & filters.user(SUDOERS)
)
async def scanNLP(_, message: Message):
    if not message.reply_to_message:
        return await edit_or_reply(
            message, text="Reply to a message to scan it."
        )
    r = message.reply_to_message
    text = r.text or r.caption
    if not text:
        return await edit_or_reply(message, text="Can't scan that")
    data = await arq.nlp(text)
    data = data.result[0]
    msg = f"""
**Is Spam:** {data.is_spam}
**Spam Probability:** {data.spam_probability} %
**Spam:** {data.spam}
**Ham:** {data.ham}
**Profanity:** {data.profanity}
"""
    await edit_or_reply(message, text=msg)

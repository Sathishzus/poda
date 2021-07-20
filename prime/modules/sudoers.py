import asyncio
import os
import subprocess
import time

import psutil
from pyrogram import filters
from pyrogram.errors import FloodWait

from prime import (BOT_ID, GBAN_LOG_GROUP_ID, SUDOERS, USERBOT_USERNAME, BOT_NAME ,
                 app, bot_start_time)
from prime.core.decorators.errors import capture_err
from prime.utils import formatter
from prime.utils.dbfunctions import (add_gban_user, get_served_chats,
                                   is_gbanned_user, remove_gban_user,
                                   start_restart_stage)

__MODULE__ = "Sudoers"




# Gban


@app.on_message(filters.command("smartgban") & filters.user(SUDOERS))
@capture_err
async def ban_globally(_, message):
    if not message.reply_to_message:
        if len(message.command) < 3:
            return await message.reply_text(
                "**Usage:**\n/gban [USERNAME | USER_ID] [REASON]"
            )
        user = message.text.split(None, 2)[1]
        reason = message.text.split(None, 2)[2]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        from_user = message.from_user
        if user.id == from_user.id:
            await message.reply_text(
                "You want to gban yourself? FOOL!"
            )
        elif user.id == BOT_ID:
            await message.reply_text(
                "Should i gban myself? I'm not fool like you, HUMAN!"
            )
        elif user.id in SUDOERS:
            await message.reply_text(
                "You want to ban a sudo user? GET REKT!!"
            )
        else:
            served_chats = await get_served_chats()
            m = await message.reply_text(
                f"**Initializing {BOT_NAME} Global Ban Sequence To Add Restrictions On {user.mention}**"
                + f" **This Action Should Take About {len(served_chats)} Seconds.**"
            )
            await add_gban_user(user.id)
            number_of_chats = 0
            for served_chat in served_chats:
                try:
                    await app.kick_chat_member(
                        served_chat["chat_id"], user.id
                    )
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except Exception:
                    pass
            try:
                await app.send_message(
                    user.id,
                    f"Hello, You have been globally banned by {from_user.mention},"
                    + " You can appeal for this ban in @JokerSupportZ.",
                )
            except Exception:
                pass
            await m.edit(f"Banned {user.mention} Globally!")
            ban_text = f"""
__**#SMARTGBAN**__
**Origin:** {message.chat.title} [`{message.chat.id}`]
**Admin:** {from_user.mention}
**Banned User:** {user.mention}
**Banned User ID:** `{user.id}`
**Reason:** __{reason}__
**Chats Affected:** `{number_of_chats}`"""
            try:
                m2 = await app.send_message(
                    GBAN_LOG_GROUP_ID,
                    text=ban_text,
                    disable_web_page_preview=True,
                )
                await m.edit(
                    f"Banned {user.mention} Globally!\nAction Log: {m2.link}",
                    disable_web_page_preview=True,
                )
            except Exception:
                await message.reply_text(
                    "User Gbanned, But This Gban Wasn't Logged, Add Bot In GBAN_LOG_GROUP"
                )
                return
        return
    if len(message.command) < 2:
        await message.reply_text("**Usage:**\n/gban [REASON]")
        return
    reason = message.text.strip().split(None, 1)[1]
    from_user_id = message.from_user.id
    from_user_mention = message.from_user.mention
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    if user_id == from_user_id:
        await message.reply_text("You want to gban yourself? FOOL!")
    elif user_id == BOT_ID:
        await message.reply_text(
            "Should i gban myself? I'm not fool like you, HUMAN!"
        )
    elif user_id in SUDOERS:
        await message.reply_text(
            "You want to ban a sudo user? GET REKT!!"
        )
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if is_gbanned:
            await message.reply_text(
                "He's already gbanned, why bully him?"
            )
        else:
            served_chats = await get_served_chats()
            m = await message.reply_text(
                f"**Initializing ✵ 𝕵𝖔𝖐𝖊𝖗 𝕭𝖔𝖙 ✵ Global Ban Sequence To Add Restrictions On {mention}**"
                + f" **This Action Should Take About {len(served_chats)} Seconds.**"
            )
            number_of_chats = 0
            for served_chat in served_chats:
                try:
                    await app.kick_chat_member(
                        served_chat["chat_id"], user_id
                    )
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except Exception:
                    pass
            await add_gban_user(user_id)
            try:
                await app.send_message(
                    user_id,
                    f"""
Hello, You have been globally banned by {from_user_mention},
You can appeal for this ban in Support Chat.""",
                )
            except Exception:
                pass
            await m.edit(f"Banned {mention} Globally!")
            ban_text = f"""
__**#SMARTGBAN**__
**Origin:** {message.chat.title} [`{message.chat.id}`]
**Admin:** {from_user_mention}
**Banned User:** {mention}
**Banned User ID:** `{user_id}`
**Reason:** __{reason}__
**Chats Affected:** `{number_of_chats}`"""
            try:
                m2 = await app.send_message(
                    GBAN_LOG_GROUP_ID,
                    text=ban_text,
                    disable_web_page_preview=True,
                )
                await m.edit(
                    f"Banned {mention} Globally!\nAction Log: {m2.link}",
                    disable_web_page_preview=True,
                )
            except Exception:
                await message.reply_text(
                    "User Gbanned, But This Gban Wasn't Logged, Add Bot In GBAN_LOG_GROUP"
                )


# Ungban


@app.on_message(filters.command("smartungban") & filters.user(SUDOERS))
@capture_err
async def unban_globally(_, message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "Reply to a user's message or give username/user_id."
            )
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        from_user = message.from_user
        if user.id == from_user.id:
            await message.reply_text(
                "You want to ungban yourself? FOOL!"
            )
        elif user.id == BOT_ID:
            await message.reply_text(
                "Should i ungban myself? But i'm not gbanned."
            )
        elif user.id in SUDOERS:
            await message.reply_text(
                "Sudo users can't be gbanned/ungbanned."
            )
        else:
            is_gbanned = await is_gbanned_user(user.id)
            if not is_gbanned:
                await message.reply_text(
                    "He's already free, why bully him?"
                )
            else:
                await remove_gban_user(user.id)
                await message.reply_text(
                    f"Unbanned {user.mention} Globally!"
                )
        return

    from_user_id = message.from_user.id
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    if user_id == from_user_id:
        await message.reply_text("You want to ungban yourself? FOOL!")
    elif user_id == BOT_ID:
        await message.reply_text(
            "Should i ungban myself? But i'm not gbanned."
        )
    elif user_id in SUDOERS:
        await message.reply_text(
            "Sudo users can't be gbanned/ungbanned."
        )
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if not is_gbanned:
            await message.reply_text(
                "He's already free, why bully him?"
            )
        else:
            await remove_gban_user(user_id)
            await message.reply_text(f"Unbanned {mention} Globally!")


# Broadcast


@app.on_message(
    filters.command("smartbroadcast")
    & filters.user(SUDOERS)
    & ~filters.edited
)
@capture_err
async def broadcast_message(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "**Usage**:\n/broadcast [MESSAGE]"
        )
    sleep_time = 3
    text = message.text.split(None, 1)[1]
    sent = 0
    schats = await get_served_chats()
    chats = [int(chat["chat_id"]) for chat in schats]
    m = await message.reply_text(
        f"Broadcast in progress, will take {len(chats) * sleep_time} seconds."
    )
    for i in chats:
        try:
            await app.send_message(i, text=text)
            await asyncio.sleep(sleep_time)
            sent += 1
        except FloodWait as e:
            await asyncio.sleep(int(e.x))
        except Exception:
            pass
    await m.edit(f"**Broadcasted Message In {sent} Chats.**")


# Update


@app.on_message(filters.command("update") & filters.user(SUDOERS))
async def update_restart(_, message):
    try:
        await message.reply_text(
            f'```{subprocess.check_output(["git", "pull"]).decode("UTF-8")}```'
        )
    except Exception as e:
        return await message.reply_text(str(e))
    m = await message.reply_text(
        "**Updated with default branch, restarting now.**"
    )
    await start_restart_stage(m.chat.id, m.message_id)
    os.execvp("python3.9", ["python3.9", "-m", "prime"])

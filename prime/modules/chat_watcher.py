from prime import app
from prime.utils.dbfunctions import (add_served_chat, add_served_user,
                                   blacklisted_chats, is_served_chat,
                                   is_served_user)
from prime.utils.filter_groups import chat_watcher_group


@app.on_message(group=chat_watcher_group)
async def chat_watcher_func(_, message):
    chat_id = message.chat.id
    blacklisted_chats_list = await blacklisted_chats()
    if chat_id:
        if chat_id in blacklisted_chats_list:
            return await app.leave_chat(chat_id)
    if chat_id:
        await add_served_chat(chat_id)
    if message.from_user:
        user_id = message.from_user.id
        await add_served_user(user_id)

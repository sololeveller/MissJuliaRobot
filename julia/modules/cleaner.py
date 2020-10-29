import html

from telegram import Update, ParseMode
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    run_async,
    CallbackContext,
)
from julia import dispatcher, CustomCommandHandler

from julia.modules.helper_funcs.chat_status import bot_can_delete, user_can_change
from julia.modules.sql import cleaner_sql as sql
from pymongo import MongoClient
from julia import MONGO_DB_URI

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["test"]
approved_users = db.approve

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["test"]
approved_users = db.approve

CMD_STARTERS = "/"

BLUE_TEXT_CLEAN_GROUP = 15
CommandHandlerList = (
    CommandHandler,
    CustomCommandHandler,
)

command_list = [
    "cleanbluetext",
    "ignorecleanbluetext",
    "unignorecleanbluetext",
    "listcleanbluetext",
    "ignoreglobalcleanbluetext",
    "unignoreglobalcleanbluetext" "start",
    "help",
    "settings",
    "donate",
]

for handler_list in dispatcher.handlers:
    for handler in dispatcher.handlers[handler_list]:
        if any(isinstance(handler, cmd_handler) for cmd_handler in CommandHandlerList):
            command_list += handler.command


@run_async
def clean_blue_text_must_click(update: Update, context: CallbackContext):
    # sourcery skip: merge-nested-ifs, move-assign

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user
    member = chat.get_member(user.id)
    chats = approved_users.find({})
    for c in chats:
        iiid = c["id"]
        usersss = c["user"]
        if str(user.id) in str(usersss) and str(chat.id) in str(iiid):
            return
    if user.id == context.bot.id:
        return
    if user.id == 1087968824:
        return
    if member.status in ("administrator", "creator"):
        return

    if chat.get_member(context.bot.id).can_delete_messages:
        if sql.is_enabled(chat.id):
            fst_word = message.text.strip().split(None, 1)[0]

            if len(fst_word) > 1 and any(
                fst_word.startswith(start) for start in CMD_STARTERS
            ):

                command = fst_word[1:].split("@")
                chat = update.effective_chat

                ignored = sql.is_command_ignored(chat.id, command[0])
                if ignored:
                    return

                if command[0] not in command_list:
                    message.delete()


@run_async
@bot_can_delete
@user_can_change
def set_blue_text_must_click(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    message = update.effective_message
    if len(args) >= 1:
        val = args[0].lower()
        if val in ("off", "no"):
            sql.set_cleanbt(chat.id, False)
            reply = "Bluetext cleaning has been disabled for <b>{}</b>".format(
                html.escape(chat.title)
            )
            message.reply_text(reply, parse_mode=ParseMode.HTML)

        elif val in ("yes", "on"):
            sql.set_cleanbt(chat.id, True)
            reply = "Bluetext cleaning has been enabled for <b>{}</b>".format(
                html.escape(chat.title)
            )
            message.reply_text(reply, parse_mode=ParseMode.HTML)

        else:
            reply = "Invalid argument.Accepted values are 'yes', 'on', 'no', 'off'"
            message.reply_text(reply)
    else:
        clean_status = sql.is_enabled(chat.id)
        clean_status = "Enabled" if clean_status else "Disabled"
        reply = "Bluetext cleaning for <b>{}</b> : <b>{}</b>".format(
            chat.title, clean_status
        )
        message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
@user_can_change
def add_bluetext_ignore(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    chat = update.effective_chat

    if len(args) >= 1:
        val = args[0].lower()
        added = sql.chat_ignore_command(chat.id, val)
        if added:
            reply = "<b>{}</b> has been added to bluetext cleaner ignore list.".format(
                args[0]
            )
        else:
            reply = "Command is already ignored."
        message.reply_text(reply, parse_mode=ParseMode.HTML)

    else:
        reply = "No command supplied to be ignored."
        message.reply_text(reply)


@run_async
@user_can_change
def remove_bluetext_ignore(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    chat = update.effective_chat

    if len(args) >= 1:
        val = args[0].lower()
        removed = sql.chat_unignore_command(chat.id, val)
        if removed:
            reply = (
                "<b>{}</b> has been removed from bluetext cleaner ignore list.".format(
                    args[0]
                )
            )
        else:
            reply = "Command isn't ignored currently."
        message.reply_text(reply, parse_mode=ParseMode.HTML)

    else:
        reply = "No command supplied to be unignored."
        message.reply_text(reply)


@run_async
@user_can_change
def add_bluetext_ignore_global(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    if len(args) >= 1:
        val = args[0].lower()
        added = sql.global_ignore_command(val)
        if added:
            reply = "<b>{}</b> has been added to global bluetext cleaner ignore list.".format(
                args[0]
            )
        else:
            reply = "Command is already ignored."
        message.reply_text(reply, parse_mode=ParseMode.HTML)

    else:
        reply = "No command supplied to be ignored."
        message.reply_text(reply)


@run_async
@user_can_change
def remove_bluetext_ignore_global(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    if len(args) >= 1:
        val = args[0].lower()
        removed = sql.global_unignore_command(val)
        if removed:
            reply = "<b>{}</b> has been removed from global bluetext cleaner ignore list.".format(
                args[0]
            )
        else:
            reply = "Command isn't ignored currently."
        message.reply_text(reply, parse_mode=ParseMode.HTML)

    else:
        reply = "No command supplied to be unignored."
        message.reply_text(reply)


@run_async
@user_can_change
def bluetext_ignore_list(update: Update, _):
    message = update.effective_message
    chat = update.effective_chat

    global_ignored_list, local_ignore_list = sql.get_all_ignored(chat.id)
    text = ""

    if global_ignored_list:
        text = "The following commands are currently ignored globally from bluetext cleaning :\n"

        for x in global_ignored_list:
            text += f" - <code>{x}</code>\n"

    if local_ignore_list:
        text += "\nThe following commands are currently ignored locally from bluetext cleaning :\n"

        for x in local_ignore_list:
            text += f" - <code>{x}</code>\n"

    if text == "":
        text = "No commands are currently ignored from bluetext cleaning."
        message.reply_text(text)
        return

    message.reply_text(text, parse_mode=ParseMode.HTML)
    return


__help__ = """
 - /setflood <number/off>: set the number of messages to take action on a user for flooding
 - /setfloodmode <mute/ban/kick/tban/tmute>: select the valid action eg. /setfloodmode tmute 5m
 - /flood: gets the current antiflood settings
 - /cleanservice <on/off>: clean telegram's join/left message
 - /cleanbluetext <on/off/yes/no>: clean commands from non-admins after sending
 - /ignorecleanbluetext <word>: prevent auto cleaning of the command
 - /unignorecleanbluetext <word>: remove prevent auto cleaning of the command
 - /listcleanbluetext: list currently whitelisted commands
 - /profanity on/off: filters all explict/abusive words sent by non admins also filters explicit/porn images
"""

SET_CLEAN_BLUE_TEXT_HANDLER = CommandHandler(
    "cleanbluetext", set_blue_text_must_click, pass_args=True
)
ADD_CLEAN_BLUE_TEXT_HANDLER = CommandHandler(
    "ignorecleanbluetext", add_bluetext_ignore, pass_args=True
)
REMOVE_CLEAN_BLUE_TEXT_HANDLER = CommandHandler(
    "unignorecleanbluetext", remove_bluetext_ignore, pass_args=True
)
ADD_CLEAN_BLUE_TEXT_GLOBAL_HANDLER = CommandHandler(
    "ignoreglobalcleanbluetext", add_bluetext_ignore_global, pass_args=True
)
REMOVE_CLEAN_BLUE_TEXT_GLOBAL_HANDLER = CommandHandler(
    "unignoreglobalcleanbluetext", remove_bluetext_ignore_global, pass_args=True
)
LIST_CLEAN_BLUE_TEXT_HANDLER = CommandHandler("listcleanbluetext", bluetext_ignore_list)
CLEAN_BLUE_TEXT_HANDLER = MessageHandler(
    Filters.command & Filters.group, clean_blue_text_must_click
)

dispatcher.add_handler(SET_CLEAN_BLUE_TEXT_HANDLER)
dispatcher.add_handler(ADD_CLEAN_BLUE_TEXT_HANDLER)
dispatcher.add_handler(REMOVE_CLEAN_BLUE_TEXT_HANDLER)
dispatcher.add_handler(ADD_CLEAN_BLUE_TEXT_GLOBAL_HANDLER)
dispatcher.add_handler(REMOVE_CLEAN_BLUE_TEXT_GLOBAL_HANDLER)
dispatcher.add_handler(LIST_CLEAN_BLUE_TEXT_HANDLER)
dispatcher.add_handler(CLEAN_BLUE_TEXT_HANDLER, BLUE_TEXT_CLEAN_GROUP)

__mod_name__ = "Anti-Spam 🚦"

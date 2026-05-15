‎"""
‎Telegram Group Management Bot
‎Features: Bot Menu, Photo Banner, Inline Buttons, Full Moderation
‎"""
‎
‎import logging
‎from telegram import Update, ChatPermissions, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
‎from telegram.ext import (
‎    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
‎    filters, ContextTypes
‎)
‎
‎# ─── Config ─────────────────────────────────────────────────────────────────
‎TOKEN      = "8441600863:AAF1NqmbyC_cLjR8sCIMyV5LNkKmOgIVUqE"                   # @BotFather থেকে নাও
‎BANNER_URL = "https://files.catbox.moe/eux4xg.jpg"    # তোমার photo URL দাও
‎
‎# ─── Logging ─────────────────────────────────────────────────────────────────
‎logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
‎logger = logging.getLogger(__name__)
‎
‎# ─── Storage ─────────────────────────────────────────────────────────────────
‎warn_db    = {}   # {chat_id: {user_id: count}}
‎filter_db  = {}   # {chat_id: {keyword: reply}}
‎notes_db   = {}   # {chat_id: {name: text}}
‎welcome_db = {}   # {chat_id: message}
‎locked_db  = {}   # {chat_id: [types]}
‎MAX_WARNS  = 3
‎
‎# ─── Helpers ─────────────────────────────────────────────────────────────────
‎async def is_admin(update, context, user_id):
‎    member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
‎    return member.status in ["administrator", "creator"]
‎
‎async def get_target_user(update, context):
‎    msg = update.effective_message
‎    if msg.reply_to_message:
‎        return msg.reply_to_message.from_user
‎    if context.args:
‎        try:
‎            return await context.bot.get_chat(context.args[0])
‎        except Exception:
‎            await msg.reply_text("❌ User not found.")
‎            return None
‎    await msg.reply_text("❌ Reply to a user or give a username/ID.")
‎    return None
‎
‎def mention(user):
‎    return f"[{user.first_name}](tg://user?id={user.id})"
‎
‎# ══════════════════════════════════════════════════════════════════════════════
‎# BOT MENU — Telegram "/" চাপলে সব command দেখাবে
‎# ══════════════════════════════════════════════════════════════════════════════
‎async def set_bot_menu(app):
‎    commands = [
‎        BotCommand("start",        "🏠 Start the bot),
‎        BotCommand("help",         "📖 All command check"),
‎        BotCommand("ping",         "🏓 Check if bot is alive"),
‎        BotCommand("id",           "🆔 Chat/User ID check"),
‎        BotCommand("info",         "ℹ️ User info"),
‎        BotCommand("ban",          "🔨 User ban"),
‎        BotCommand("unban",        "✅ User unban"),
‎        BotCommand("kick",         "👢 User kick"),
‎        BotCommand("mute",         "🔇 User mute"),
‎        BotCommand("unmute",       "🔊 User unmute"),
‎        BotCommand("warn",         "⚠️ Warning"),
‎        BotCommand("unwarn",       "🗑️ Warn remove"),
‎        BotCommand("warns",        "📊 Warn count see"),
‎        BotCommand("promote",      "⭐ Make Admin"),
‎        BotCommand("demote",       "🔻  Remove Admin"),
‎        BotCommand("save",         "📌 Note save"),
‎        BotCommand("get",          "📂 Note check"),
‎        BotCommand("notes",        "📋 All notes check"),
‎        BotCommand("clear",        "🗑️ Note Remove"),
‎        BotCommand("filter",       "🔍 Filter add"),
‎        BotCommand("filters",      "📃 see all filters"),
‎        BotCommand("stop",         "❌ Filter remove"),
‎        BotCommand("setwelcome",   "👋 Welcome message set"),
‎        BotCommand("welcome",      "💬 Welcome message check"),
‎        BotCommand("clearwelcome", "🗑️ Welcome remove"),
‎        BotCommand("lock",         "🔒 Content lock now"),
‎        BotCommand("unlock",       "🔓 Content unlock now"),
‎        BotCommand("locks",        "🔐 Lock status check"),
‎    ]
‎    await app.bot.set_my_commands(commands)
‎    logger.info("✅ Bot menu registered!")
‎
‎# ══════════════════════════════════════════════════════════════════════════════
‎# START — Photo banner + Inline menu buttons
‎# ══════════════════════════════════════════════════════════════════════════════
‎async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎    keyboard = InlineKeyboardMarkup([
‎        [
‎            InlineKeyboardButton("📖 All Commands", callback_data="help"),
‎            InlineKeyboardButton("👮 Moderation",   callback_data="mod"),
‎        ],
‎        [
‎            InlineKeyboardButton("📌 Notes",         callback_data="notes_help"),
‎            InlineKeyboardButton("🔍 Filters",       callback_data="filters_help"),
‎        ],
‎        [
‎            InlineKeyboardButton("🔒 Locks",         callback_data="locks_help"),
‎            InlineKeyboardButton("👋 Welcome",        callback_data="welcome_help"),
‎        ],
‎    ])
‎    caption = (
‎        "👋 *Hello! I'm your Group Manager Bot.*\n\n"
‎        "I help you manage your Telegram group:\n\n"
‎        "🔨 *Moderation* — Ban, Kick, Mute, Warn\n"
‎        "📌 *Notes* — Save & retrieve group notes\n"
‎        "🔍 *Filters* — Auto-reply to keywords\n"
‎        "👋 *Welcome* — Custom welcome messages\n"
‎        "🔒 *Locks* — Block sticker/gif/media\n\n"
‎        "👇 Tap a button or type /help"
‎    )
‎    try:
‎        await update.message.reply_photo(
‎            photo=BANNER_URL,
‎            caption=caption,
‎            parse_mode="Markdown",
‎            reply_markup=keyboard
‎        )
‎    except Exception:
‎        # If photo fails, send text instead
‎        await update.message.reply_text(caption, parse_mode="Markdown", reply_markup=keyboard)
‎
‎# ── Help texts for inline buttons ────────────────────────────────────────────
‎HELP_TEXTS = {
‎    "help": (
‎        "📖 *All Commands:*\n\n"
‎        "👮 /ban /unban /kick\n"
‎        "🔇 /mute /unmute\n"
‎        "⚠️ /warn /unwarn /warns\n"
‎        "⭐ /promote /demote\n"
‎        "📌 /save /get /notes /clear\n"
‎        "🔍 /filter /filters /stop\n"
‎        "👋 /setwelcome /welcome /clearwelcome\n"
‎        "🔒 /lock /unlock /locks\n"
‎        "ℹ️ /info /id /ping"
‎    ),
‎    "mod": (
‎        "👮 *Moderation Commands:*\n\n"
‎        "/ban — Reply to user ban\n"
‎        "/unban — User unban\n"
‎        "/kick — User kick\n"
‎        "/mute — User mute\n"
‎        "/unmute — Mute remove\n"
‎        "/warn — Warning give (3 = auto ban)\n"
‎        "/unwarn — 1 warn remove\n"
‎        "/warns — Warn count\n"
‎        "/promote — Make Admin\n"
‎        "/demote — Remove Admin"
‎    ),
‎    "notes_help": (
‎        "📌 *Notes System:*\n\n"
‎        "/save <n> <text> — Note save\n"
‎        "/get <n> — Note check\n"
‎        "/notes — all notes list\n"
‎        "/clear <n> — Note remove\n\n"
‎        "Example:\n"
‎        "`/save rules No spam!`\n"
‎        "`/get rules`"
‎    ),
‎    "filters_help": (
‎        "🔍 *Filters System:*\n\n"
‎        "/filter <word> <reply> — Filter add\n"
‎        "/filters — all active filters\n"
‎        "/stop <word> — Filter remove\n\n"
‎        "Example:\n"
‎        "`/filter hello Hi there! 👋`\n"
‎        "Now if someone writes 'hello' the bot will reply!"
‎    ),
‎    "locks_help": (
‎        "🔒 *Lock System:*\n\n"
‎        "/lock sticker — Lock sticker\n"
‎        "/lock gif — Lock GIF\n"
‎        "/lock media — Lock Photo/video\n"
‎        "/lock text — Lock Text\n"
‎        "/lock all — All lock\n"
‎        "/unlock <type> — Unlock\n"
‎        "/locks — Lock status check"
‎    ),
‎    "welcome_help": (
‎        "👋 *Welcome System:*\n\n"
‎        "/setwelcome <msg> — Welcome add\n"
‎        "  • `{name}` = user name\n"
‎        "/welcome — Current welcome দেখো\n"
‎        "/clearwelcome — Remove Welcome\n\n"
‎        "Example:\n"
‎        "`/setwelcome Welcome {name}! 🎉`"
‎    ),
‎}
‎
‎async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎    query = update.callback_query
‎    await query.answer()
‎    text = HELP_TEXTS.get(query.data, "❌ Unknown.")
‎    back = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="help")]])
‎    try:
‎        await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=back)
‎    except Exception:
‎        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=back)
‎
‎# ══════════════════════════════════════════════════════════════════════════════
‎# BASIC
‎# ══════════════════════════════════════════════════════════════════════════════
‎async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎    await update.message.reply_text(HELP_TEXTS["help"], parse_mode="Markdown")
‎
‎async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎    await update.message.reply_text("🏓 Pong! Bot is alive.")
‎
‎async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎    msg = update.effective_message
‎    user = update.effective_user
‎    chat = update.effective_chat
‎    if msg.reply_to_message:
‎        t = msg.reply_to_message.from_user
‎        await msg.reply_text(f"👤 User ID: `{t.id}`", parse_mode="Markdown")
‎    else:
‎        await msg.reply_text(f"👤 Your ID: `{user.id}`\n💬 Chat ID: `{chat.id}`", parse_mode="Markdown")
‎
‎async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎    msg = update.effective_message
‎    user = msg.reply_to_message.from_user if msg.reply_to_message else update.effective_user
‎    try:
‎        member = await context.bot.get_chat_member(update.effective_chat.id, user.id)
‎        status = member.status.capitalize()
‎    except Exception:
‎        status = "Unknown"
‎    await msg.reply_text(
‎        f"ℹ️ *User Info:*\n\n"
‎        f"👤 Name: {user.full_name}\n"
‎        f"🆔 ID: `{user.id}`\n"
‎        f"📛 Username: @{user.username or 'N/A'}\n"
‎        f"🔖 Status: {status}\n"
‎        f"🤖 Is Bot: {'Yes' if user.is_bot else 'No'}",
‎        parse_mode="Markdown"
‎    )
‎
‎# ══════════════════════════════════════════════════════════════════════════════
‎# MODERATION
‎# ══════════════════════════════════════════════════════════════════════════════
‎async def ban(update, context):
‎    msg = update.effective_message
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    user = await get_target_user(update, context)
‎    if not user: return
‎    reason = " ".join(context.args[1:]) if context.args and len(context.args) > 1 else "No reason"
‎    try:
‎        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
‎        await msg.reply_text(f"🔨 *Banned:* {mention(user)}\n📝 {reason}", parse_mode="Markdown")
‎    except Exception as e:
‎        await msg.reply_text(f"❌ Failed: {e}")
‎
‎async def unban(update, context):
‎    msg = update.effective_message
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    user = await get_target_user(update, context)
‎    if not user: return
‎    try:
‎        await context.bot.unban_chat_member(update.effective_chat.id, user.id)
‎        await msg.reply_text(f"✅ *Unbanned:* {mention(user)}", parse_mode="Markdown")
‎    except Exception as e:
‎        await msg.reply_text(f"❌ Failed: {e}")
‎
‎async def kick(update, context):
‎    msg = update.effective_message
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    user = await get_target_user(update, context)
‎    if not user: return
‎    try:
‎        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
‎        await context.bot.unban_chat_member(update.effective_chat.id, user.id)
‎        await msg.reply_text(f"👢 *Kicked:* {mention(user)}", parse_mode="Markdown")
‎    except Exception as e:
‎        await msg.reply_text(f"❌ Failed: {e}")
‎
‎async def mute(update, context):
‎    msg = update.effective_message
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    user = await get_target_user(update, context)
‎    if not user: return
‎    try:
‎        await context.bot.restrict_chat_member(
‎            update.effective_chat.id, user.id,
‎            permissions=ChatPermissions(can_send_messages=False)
‎        )
‎        await msg.reply_text(f"🔇 *Muted:* {mention(user)}", parse_mode="Markdown")
‎    except Exception as e:
‎        await msg.reply_text(f"❌ Failed: {e}")
‎
‎async def unmute(update, context):
‎    msg = update.effective_message
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    user = await get_target_user(update, context)
‎    if not user: return
‎    try:
‎        await context.bot.restrict_chat_member(
‎            update.effective_chat.id, user.id,
‎            permissions=ChatPermissions(
‎                can_send_messages=True, can_send_media_messages=True,
‎                can_send_polls=True, can_send_other_messages=True,
‎                can_add_web_page_previews=True,
‎            )
‎        )
‎        await msg.reply_text(f"🔊 *Unmuted:* {mention(user)}", parse_mode="Markdown")
‎    except Exception as e:
‎        await msg.reply_text(f"❌ Failed: {e}")
‎
‎async def promote(update, context):
‎    msg = update.effective_message
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    user = await get_target_user(update, context)
‎    if not user: return
‎    try:
‎        await context.bot.promote_chat_member(
‎            update.effective_chat.id, user.id,
‎            can_delete_messages=True, can_restrict_members=True,
‎            can_pin_messages=True, can_manage_chat=True,
‎        )
‎        await msg.reply_text(f"⭐ *Promoted:* {mention(user)}", parse_mode="Markdown")
‎    except Exception as e:
‎        await msg.reply_text(f"❌ Failed: {e}")
‎
‎async def demote(update, context):
‎    msg = update.effective_message
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    user = await get_target_user(update, context)
‎    if not user: return
‎    try:
‎        await context.bot.promote_chat_member(
‎            update.effective_chat.id, user.id,
‎            can_delete_messages=False, can_restrict_members=False,
‎            can_pin_messages=False, can_manage_chat=False,
‎        )
‎        await msg.reply_text(f"🔻 *Demoted:* {mention(user)}", parse_mode="Markdown")
‎    except Exception as e:
‎        await msg.reply_text(f"❌ Failed: {e}")
‎
‎# ══════════════════════════════════════════════════════════════════════════════
‎# WARNS
‎# ══════════════════════════════════════════════════════════════════════════════
‎async def warn(update, context):
‎    msg = update.effective_message
‎    chat = update.effective_chat
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    user = await get_target_user(update, context)
‎    if not user: return
‎    reason = " ".join(context.args[1:]) if context.args and len(context.args) > 1 else "No reason"
‎    cid, uid = str(chat.id), str(user.id)
‎    if cid not in warn_db: warn_db[cid] = {}
‎    warn_db[cid][uid] = warn_db[cid].get(uid, 0) + 1
‎    count = warn_db[cid][uid]
‎    if count >= MAX_WARNS:
‎        await context.bot.ban_chat_member(chat.id, user.id)
‎        await msg.reply_text(f"⛔ {mention(user)} — *{MAX_WARNS} warns → Auto Banned!*", parse_mode="Markdown")
‎        warn_db[cid][uid] = 0
‎    else:
‎        await msg.reply_text(
‎            f"⚠️ *Warned:* {mention(user)}\n📝 {reason}\n📊 {count}/{MAX_WARNS}",
‎            parse_mode="Markdown"
‎        )
‎
‎async def unwarn(update, context):
‎    msg = update.effective_message
‎    chat = update.effective_chat
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    user = await get_target_user(update, context)
‎    if not user: return
‎    cid, uid = str(chat.id), str(user.id)
‎    if warn_db.get(cid, {}).get(uid, 0) > 0:
‎        warn_db[cid][uid] -= 1
‎        await msg.reply_text(f"✅ 1 warn removed. Now: {warn_db[cid][uid]}/{MAX_WARNS}")
‎    else:
‎        await msg.reply_text("ℹ️ No warns.")
‎
‎async def warns(update, context):
‎    msg = update.effective_message
‎    chat = update.effective_chat
‎    user = (await get_target_user(update, context)) or update.effective_user
‎    count = warn_db.get(str(chat.id), {}).get(str(user.id), 0)
‎    await msg.reply_text(f"📊 *Warns for* {mention(user)}: *{count}/{MAX_WARNS}*", parse_mode="Markdown")
‎
‎# ══════════════════════════════════════════════════════════════════════════════
‎# NOTES
‎# ══════════════════════════════════════════════════════════════════════════════
‎async def save_note(update, context):
‎    msg = update.effective_message
‎    chat = update.effective_chat
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    if not context.args or len(context.args) < 2:
‎        return await msg.reply_text("Usage: /save <n> <text>")
‎    name, text = context.args[0].lower(), " ".join(context.args[1:])
‎    cid = str(chat.id)
‎    if cid not in notes_db: notes_db[cid] = {}
‎    notes_db[cid][name] = text
‎    await msg.reply_text(f"📌 Note *'{name}'* saved!", parse_mode="Markdown")
‎
‎async def get_note(update, context):
‎    msg = update.effective_message
‎    if not context.args:
‎        return await msg.reply_text("Usage: /get <n>")
‎    name = context.args[0].lower()
‎    note = notes_db.get(str(update.effective_chat.id), {}).get(name)
‎    if note:
‎        await msg.reply_text(f"📌 *{name}:*\n{note}", parse_mode="Markdown")
‎    else:
‎        await msg.reply_text(f"❌ Note *'{name}'* not found.", parse_mode="Markdown")
‎
‎async def list_notes(update, context):
‎    notes = notes_db.get(str(update.effective_chat.id), {})
‎    if not notes: return await update.message.reply_text("📭 No notes saved.")
‎    await update.message.reply_text("📋 *Notes:*\n" + "\n".join(f"• `{n}`" for n in notes), parse_mode="Markdown")
‎
‎async def clear_note(update, context):
‎    msg = update.effective_message
‎    chat = update.effective_chat
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    if not context.args: return await msg.reply_text("Usage: /clear <n>")
‎    name = context.args[0].lower()
‎    cid = str(chat.id)
‎    if notes_db.get(cid, {}).pop(name, None):
‎        await msg.reply_text(f"🗑️ Note *'{name}'* deleted.", parse_mode="Markdown")
‎    else:
‎        await msg.reply_text(f"❌ Not found.", parse_mode="Markdown")
‎
‎# ══════════════════════════════════════════════════════════════════════════════
‎# FILTERS
‎# ══════════════════════════════════════════════════════════════════════════════
‎async def add_filter(update, context):
‎    msg = update.effective_message
‎    chat = update.effective_chat
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    if not context.args or len(context.args) < 2:
‎        return await msg.reply_text("Usage: /filter <word> <reply>")
‎    keyword, reply = context.args[0].lower(), " ".join(context.args[1:])
‎    cid = str(chat.id)
‎    if cid not in filter_db: filter_db[cid] = {}
‎    filter_db[cid][keyword] = reply
‎    await msg.reply_text(f"✅ Filter *'{keyword}'* added!", parse_mode="Markdown")
‎
‎async def list_filters(update, context):
‎    fl = filter_db.get(str(update.effective_chat.id), {})
‎    if not fl: return await update.message.reply_text("📭 No filters.")
‎    await update.message.reply_text("🔍 *Filters:*\n" + "\n".join(f"• `{k}`" for k in fl), parse_mode="Markdown")
‎
‎async def stop_filter(update, context):
‎    msg = update.effective_message
‎    chat = update.effective_chat
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    if not context.args: return await msg.reply_text("Usage: /stop <word>")
‎    keyword = context.args[0].lower()
‎    cid = str(chat.id)
‎    if filter_db.get(cid, {}).pop(keyword, None):
‎        await msg.reply_text(f"🗑️ Filter *'{keyword}'* removed.", parse_mode="Markdown")
‎    else:
‎        await msg.reply_text("❌ Not found.", parse_mode="Markdown")
‎
‎async def check_filters(update, context):
‎    text = update.effective_message.text or ""
‎    for keyword, reply in filter_db.get(str(update.effective_chat.id), {}).items():
‎        if keyword in text.lower():
‎            await update.effective_message.reply_text(reply)
‎            break
‎
‎# ══════════════════════════════════════════════════════════════════════════════
‎# WELCOME
‎# ══════════════════════════════════════════════════════════════════════════════
‎async def set_welcome(update, context):
‎    msg = update.effective_message
‎    chat = update.effective_chat
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    if not context.args:
‎        return await msg.reply_text("Usage: /setwelcome <msg>  (use {name} for user's name)")
‎    welcome_db[str(chat.id)] = " ".join(context.args)
‎    await msg.reply_text("✅ Welcome message set!")
‎
‎async def show_welcome(update, context):
‎    msg = welcome_db.get(str(update.effective_chat.id), "No welcome set.")
‎    await update.message.reply_text(f"👋 *Current welcome:*\n{msg}", parse_mode="Markdown")
‎
‎async def clear_welcome(update, context):
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await update.message.reply_text("❌ Admins only.")
‎    welcome_db.pop(str(update.effective_chat.id), None)
‎    await update.message.reply_text("🗑️ Welcome cleared.")
‎
‎async def greet_new_member(update, context):
‎    chat = update.effective_chat
‎    for member in update.message.new_chat_members:
‎        if member.is_bot: continue
‎        msg = welcome_db.get(str(chat.id), f"Welcome to {chat.title}, {{name}}! 👋")
‎        await update.message.reply_text(msg.replace("{name}", member.first_name))
‎
‎# ══════════════════════════════════════════════════════════════════════════════
‎# LOCKS
‎# ══════════════════════════════════════════════════════════════════════════════
‎LOCK_TYPES = ["sticker", "gif", "media", "text", "all"]
‎
‎async def lock(update, context):
‎    msg = update.effective_message
‎    chat = update.effective_chat
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    if not context.args or context.args[0] not in LOCK_TYPES:
‎        return await msg.reply_text(f"Usage: /lock <type>\nTypes: {', '.join(LOCK_TYPES)}")
‎    t = context.args[0]; cid = str(chat.id)
‎    if cid not in locked_db: locked_db[cid] = []
‎    locked_db[cid] = LOCK_TYPES[:-1] if t == "all" else list(set(locked_db[cid] + [t]))
‎    await msg.reply_text(f"🔒 *{t.capitalize()}* locked.", parse_mode="Markdown")
‎
‎async def unlock(update, context):
‎    msg = update.effective_message
‎    chat = update.effective_chat
‎    if not await is_admin(update, context, update.effective_user.id):
‎        return await msg.reply_text("❌ Admins only.")
‎    if not context.args: return await msg.reply_text("Usage: /unlock <type>")
‎    t = context.args[0]; cid = str(chat.id)
‎    if t == "all": locked_db[cid] = []
‎    elif t in locked_db.get(cid, []): locked_db[cid].remove(t)
‎    await msg.reply_text(f"🔓 *{t.capitalize()}* unlocked.", parse_mode="Markdown")
‎
‎async def show_locks(update, context):
‎    current = locked_db.get(str(update.effective_chat.id), [])
‎    lines = [f"• {t.capitalize()}: {'🔒 Locked' if t in current else '🔓 Unlocked'}" for t in LOCK_TYPES[:-1]]
‎    await update.message.reply_text("🔐 *Lock Status:*\n" + "\n".join(lines), parse_mode="Markdown")
‎
‎async def enforce_locks(update, context):
‎    msg = update.effective_message
‎    chat = update.effective_chat
‎    locks = locked_db.get(str(chat.id), [])
‎    if await is_admin(update, context, update.effective_user.id): return
‎    if "sticker" in locks and msg.sticker:
‎        await msg.delete(); await chat.send_message("🔒 Stickers are locked.")
‎    elif "gif" in locks and msg.animation:
‎        await msg.delete(); await chat.send_message("🔒 GIFs are locked.")
‎    elif "media" in locks and (msg.photo or msg.video or msg.document or msg.audio):
‎        await msg.delete(); await chat.send_message("🔒 Media is locked.")
‎    elif "text" in locks and msg.text:
‎        await msg.delete(); await chat.send_message("🔒 Text is locked.")
‎
‎# ══════════════════════════════════════════════════════════════════════════════
‎# MAIN
‎# ══════════════════════════════════════════════════════════════════════════════
‎def main():
‎    app = Application.builder().token(TOKEN).post_init(set_bot_menu).build()
‎
‎    app.add_handler(CommandHandler("start",        start))
‎    app.add_handler(CommandHandler("help",         help_command))
‎    app.add_handler(CommandHandler("ping",         ping))
‎    app.add_handler(CommandHandler("id",           get_id))
‎    app.add_handler(CommandHandler("info",         info))
‎    app.add_handler(CommandHandler("ban",          ban))
‎    app.add_handler(CommandHandler("unban",        unban))
‎    app.add_handler(CommandHandler("kick",         kick))
‎    app.add_handler(CommandHandler("mute",         mute))
‎    app.add_handler(CommandHandler("unmute",       unmute))
‎    app.add_handler(CommandHandler("promote",      promote))
‎    app.add_handler(CommandHandler("demote",       demote))
‎    app.add_handler(CommandHandler("warn",         warn))
‎    app.add_handler(CommandHandler("unwarn",       unwarn))
‎    app.add_handler(CommandHandler("warns",        warns))
‎    app.add_handler(CommandHandler("save",         save_note))
‎    app.add_handler(CommandHandler("get",          get_note))
‎    app.add_handler(CommandHandler("notes",        list_notes))
‎    app.add_handler(CommandHandler("clear",        clear_note))
‎    app.add_handler(CommandHandler("filter",       add_filter))
‎    app.add_handler(CommandHandler("filters",      list_filters))
‎    app.add_handler(CommandHandler("stop",         stop_filter))
‎    app.add_handler(CommandHandler("setwelcome",   set_welcome))
‎    app.add_handler(CommandHandler("welcome",      show_welcome))
‎    app.add_handler(CommandHandler("clearwelcome", clear_welcome))
‎    app.add_handler(CommandHandler("lock",         lock))
‎    app.add_handler(CommandHandler("unlock",       unlock))
‎    app.add_handler(CommandHandler("locks",        show_locks))
‎
‎    app.add_handler(CallbackQueryHandler(button_callback))
‎    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_member))
‎    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_filters))
‎    app.add_handler(MessageHandler(
‎        filters.ALL & ~filters.COMMAND & ~filters.StatusUpdate.ALL,
‎        enforce_locks
‎    ))
‎
‎    print("🤖 Bot is running...")
‎    app.run_polling()
‎
‎if __name__ == "__main__":
‎    main()
‎

import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters
)

logging.basicConfig(level=logging.INFO)

# -------------------- OWNER & ADMINS --------------------
OWNER = 123456789   # <<< PUT YOUR TELEGRAM ID HERE
ADMINS = set()      # people you promote to admin

# -------------------- RANKS --------------------
RANKS = {
    1: "🔹 Rank 1 — Beginner",
    2: "🔸 Rank 2 — Novice",
    3: "⭐ Rank 3 — Skilled",
    4: "🌟 Rank 4 — Advanced",
    5: "🔥 Rank 5 — Pro",
    6: "⚡ Rank 6 — Elite",
    7: "👑 Rank 7 — Master",
    8: "💠 Rank 8 — Legend",
    9: "🌀 Rank 9 — God"
}

# -------------------- DATABASE SIMULATION --------------------
user_rank = {}
harem = {}  # harem[user_id] = [ { 'name': '', 'family': '', 'image': '' }, ... ]


# -------------------- UTILITIES --------------------
def is_admin(user_id):
    return user_id == OWNER or user_id in ADMINS


def get_rank(user_id):
    if user_id not in user_rank:
        user_rank[user_id] = 1
    return user_rank[user_id]


def add_character(user_id, name, family, image_url):
    if user_id not in harem:
        harem[user_id] = []

    harem[user_id].append({
        "name": name,
        "family": family,
        "image": image_url
    })


# -------------------- COMMANDS --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_rank[user_id] = 1

    kb = [
        [InlineKeyboardButton("💖 My Harem", callback_data="harem")],
        [InlineKeyboardButton("📊 My Rank", callback_data="rank")]
    ]

    # upload button only for admins
    if is_admin(user_id):
        kb.insert(0, [InlineKeyboardButton("📥 Upload Character", callback_data="upload")])

    await update.message.reply_text(
        "Welcome!\nYour rank: " + RANKS[1],
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != OWNER:
        await update.message.reply_text("❌ Only OWNER can add admins.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Usage: /addadmin USER_ID")
        return

    new_admin = int(context.args[0])
    ADMINS.add(new_admin)

    await update.message.reply_text(f"✅ User {new_admin} promoted to ADMIN.")


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # ---- SHOW RANK ----
    if query.data == "rank":
        await query.edit_message_text(
            f"Your Rank:\n{RANKS[get_rank(user_id)]}"
        )

    # ---- ADMIN UPLOAD ----
    elif query.data == "upload":
        if not is_admin(user_id):
            await query.edit_message_text("❌ You are not an admin.")
            return

        context.user_data["upload_mode"] = True
        await query.edit_message_text(
            "Send:\n\n`imageURL name family`",
            parse_mode="Markdown"
        )

    # ---- SHOW HAREM ----
    elif query.data == "harem":
        r = get_rank(user_id)

        if user_id not in harem or len(harem[user_id]) == 0:
            await query.edit_message_text("Your harem is empty ❌")
            return

        max_allowed = r
        allowed_list = harem[user_id][:max_allowed]

        text = "💖 Your Harem:\n\n"
        for char in allowed_list:
            text += f"• {char['name']} {char['family']}\n{char['image']}\n\n"

        await query.edit_message_text(text)


# -------------------- TEXT HANDLER --------------------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # ----- ADMIN UPLOAD MODE -----
    if context.user_data.get("upload_mode"):
        if not is_admin(user_id):
            await update.message.reply_text("❌ Only admins can upload characters.")
            return

        msg = update.message.text.split(" ")

        if len(msg) < 3:
            await update.message.reply_text("Invalid format. Use: `imageURL name family`")
            return

        image = msg[0]
        name = msg[1]
        family = msg[2]

        add_character(user_id, name, family, image)
        context.user_data["upload_mode"] = False

        await update.message.reply_text(
            f"Character added!\n{name} {family}\n{image}"
        )
        return

    # ----- NORMAL MESSAGES -----
    if user_id not in user_rank:
        user_rank[user_id] = 1

    if user_rank[user_id] < 9:
        user_rank[user_id] += 1

    await update.message.reply_text(
        f"Message received!\nYour rank: {RANKS[user_rank[user_id]]}"
    )


# -------------------- MAIN --------------------
async def main():
    app = ApplicationBuilder().token("8545099900:AAEEcFXxnk1ttoBunZlnvAeNU7QHTDomO5Q").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT, text_handler))

    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

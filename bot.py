import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import os
import random
import json
from aiohttp import web
import asyncio

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get credentials from environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
OWNER_ID = int(os.environ.get('OWNER_ID', '0'))
JOIN_LINK_1 = os.environ.get('JOIN_LINK_1', 'https://t.me/your_channel')
ADMIN_LINK = os.environ.get('ADMIN_LINK', 'https://t.me/fr_sammm11')
PORT = int(os.environ.get('PORT', '10000'))

# Store message mappings and user database
message_map = {}
USER_DB_FILE = 'users.json'

# Fun greeting messages
GREETINGS = [
    "✨ Got it! Sam will reply soon!",
    "📬 Message delivered! Hang tight!",
    "🎯 Your message is on its way to Sam!",
    "⚡ Sent! Sam will get back to you shortly!",
    "🌟 Message received! Sam will respond soon!",
    "💫 Delivered successfully! Stay tuned!",
    "🚀 Your message just landed! Sam will reply!",
    "🎨 Message sent! Sam's on it!",
    "🔔 Ding! Sam will see this soon!",
    "💌 Got your message! Sam will reply ASAP!"
]

def load_users():
    """Load user database"""
    try:
        if os.path.exists(USER_DB_FILE):
            with open(USER_DB_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_users(users):
    """Save user database"""
    try:
        with open(USER_DB_FILE, 'w') as f:
            json.dump(users, f)
    except Exception as e:
        logger.error(f"Error saving users: {e}")

users_db = load_users()

def create_menu_keyboard():
    """Create inline keyboard with menu buttons"""
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=JOIN_LINK_1)],
        [InlineKeyboardButton("👤 Contact Admin", url=ADMIN_LINK)]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    user_id = update.effective_user.id
    user = update.effective_user
    
    # Add user to database
    if str(user_id) not in users_db and user_id != OWNER_ID:
        users_db[str(user_id)] = {
            'name': user.full_name,
            'username': user.username,
            'first_seen': str(update.message.date)
        }
        save_users(users_db)
        logger.info(f"New user added: {user.full_name} ({user_id})")
    
    if user_id == OWNER_ID:
        total_users = len(users_db)
        await update.message.reply_text(
            f"👋 Welcome back, Sam! You're all set.\n\n"
            f"👥 Total Users: {total_users}\n\n"
            f"📝 Commands:\n"
            f"/broadcast <message> - Send message to all users\n"
            f"/stats - View bot statistics\n\n"
            f"Reply to any forwarded message to respond to users."
        )
    else:
        keyboard = create_menu_keyboard()
        await update.message.reply_text(
            "👋 Hi! Please send a message to Sam, he'll reply soon.\n\n"
            "Need quick access? Check out the buttons below! 👇",
            reply_markup=keyboard
        )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast command (owner only)"""
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ This command is only for the bot owner.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📢 Broadcast Usage:\n\n"
            "/broadcast <your message>\n\n"
            "Example: /broadcast Hello everyone! 👋"
        )
        return
    
    broadcast_msg = ' '.join(context.args)
    success_count = 0
    fail_count = 0
    
    status_msg = await update.message.reply_text("📡 Broadcasting message...")
    
    for user_id_str in users_db.keys():
        try:
            await context.bot.send_message(
                chat_id=int(user_id_str),
                text=f"📢 Message from Sam:\n\n{broadcast_msg}"
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send to {user_id_str}: {e}")
            fail_count += 1
    
    await status_msg.edit_text(
        f"✅ Broadcast Complete!\n\n"
        f"✓ Sent: {success_count}\n"
        f"✗ Failed: {fail_count}"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics (owner only)"""
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ This command is only for the bot owner.")
        return
    
    total_users = len(users_db)
    
    stats_text = (
        f"📊 Bot Statistics\n\n"
        f"👥 Total Users: {total_users}\n"
        f"💬 Active Conversations: {len(message_map)}\n\n"
        f"🔗 Links:\n"
        f"Channel: {JOIN_LINK_1}\n"
        f"Admin: {ADMIN_LINK}"
    )
    
    await update.message.reply_text(stats_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    user_id = update.effective_user.id
    message = update.message
    
    if user_id == OWNER_ID:
        # Owner is replying to a user
        if message.reply_to_message:
            replied_msg_id = message.reply_to_message.message_id
            
            if replied_msg_id in message_map:
                target_user_id = message_map[replied_msg_id]
                
                try:
                    # Send owner's reply to the user
                    if message.text:
                        await context.bot.send_message(
                            chat_id=target_user_id,
                            text=message.text
                        )
                    elif message.photo:
                        await context.bot.send_photo(
                            chat_id=target_user_id,
                            photo=message.photo[-1].file_id,
                            caption=message.caption
                        )
                    elif message.video:
                        await context.bot.send_video(
                            chat_id=target_user_id,
                            video=message.video.file_id,
                            caption=message.caption
                        )
                    elif message.document:
                        await context.bot.send_document(
                            chat_id=target_user_id,
                            document=message.document.file_id,
                            caption=message.caption
                        )
                    elif message.voice:
                        await context.bot.send_voice(
                            chat_id=target_user_id,
                            voice=message.voice.file_id
                        )
                    elif message.audio:
                        await context.bot.send_audio(
                            chat_id=target_user_id,
                            audio=message.audio.file_id,
                            caption=message.caption
                        )
                    
                    await message.reply_text("✅ Message sent!")
                    
                except Exception as e:
                    await message.reply_text(f"❌ Failed to send message: {str(e)}")
            else:
                await message.reply_text("⚠️ Cannot find the original sender. Please reply to a forwarded message.")
    else:
        # User is sending a message to owner
        user = update.effective_user
        username = f"@{user.username}" if user.username else "No username"
        full_name = user.full_name or "Unknown"
        
        # Add user to database if not exists
        if str(user_id) not in users_db:
            users_db[str(user_id)] = {
                'name': full_name,
                'username': user.username,
                'first_seen': str(message.date)
            }
            save_users(users_db)
        
        # Create message header
        header = (
            f"📨 New message from:\n"
            f"👤 Name: {full_name}\n"
            f"🆔 ID: {user.id}\n"
            f"📱 Username: {username}\n"
            f"{'─' * 30}\n"
        )
        
        try:
            # Forward different types of messages
            if message.text:
                sent_msg = await context.bot.send_message(
                    chat_id=OWNER_ID,
                    text=f"{header}{message.text}"
                )
            elif message.photo:
                sent_msg = await context.bot.send_photo(
                    chat_id=OWNER_ID,
                    photo=message.photo[-1].file_id,
                    caption=f"{header}{message.caption or ''}"
                )
            elif message.video:
                sent_msg = await context.bot.send_video(
                    chat_id=OWNER_ID,
                    video=message.video.file_id,
                    caption=f"{header}{message.caption or ''}"
                )
            elif message.document:
                sent_msg = await context.bot.send_document(
                    chat_id=OWNER_ID,
                    document=message.document.file_id,
                    caption=f"{header}{message.caption or ''}"
                )
            elif message.voice:
                sent_msg = await context.bot.send_voice(
                    chat_id=OWNER_ID,
                    voice=message.voice.file_id,
                    caption=header
                )
            elif message.audio:
                sent_msg = await context.bot.send_audio(
                    chat_id=OWNER_ID,
                    audio=message.audio.file_id,
                    caption=f"{header}{message.caption or ''}"
                )
            elif message.sticker:
                await context.bot.send_message(
                    chat_id=OWNER_ID,
                    text=f"{header}[Sticker received]"
                )
                sent_msg = await context.bot.send_sticker(
                    chat_id=OWNER_ID,
                    sticker=message.sticker.file_id
                )
            else:
                sent_msg = await context.bot.send_message(
                    chat_id=OWNER_ID,
                    text=f"{header}[Unsupported message type]"
                )
            
            # Store mapping for replies
            message_map[sent_msg.message_id] = user_id
            
            # Send random greeting with menu buttons
            greeting = random.choice(GREETINGS)
            keyboard = create_menu_keyboard()
            await message.reply_text(greeting, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
            await message.reply_text("❌ Sorry, there was an error sending your message. Please try again.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

# Web server to keep Render happy
async def health_check(request):
    """Health check endpoint for Render"""
    return web.Response(text="Bot is running! ✅")

async def start_web_server():
    """Start web server for Render"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"🌐 Web server started on port {PORT}")

async def main():
    """Start the bot and web server"""
    if not BOT_TOKEN or not OWNER_ID:
        logger.error("BOT_TOKEN and OWNER_ID must be set in environment variables!")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Start web server for Render
    await start_web_server()
    
    # Start the bot
    logger.info("🤖 Enhanced bot started successfully!")
    logger.info(f"👥 Loaded {len(users_db)} users from database")
    
    # Run the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    
    # Keep running forever
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        await application.stop()

if __name__ == '__main__':
    asyncio.run(main())

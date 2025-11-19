# Enhanced Telegram Message Relay Bot

A feature-rich Telegram bot that relays messages between users and the bot owner with broadcast and interactive buttons. **Optimized for Render free tier** with built-in web server!

## ✨ Features

- 📨 Forwards all user messages to the owner with sender details
- 💬 Owner can reply by responding to forwarded messages
- 📢 **Broadcast messages** to all users who started the bot
- 🎯 **Interactive buttons** (Join Channel, Contact Admin)
- 🎨 **Random fun greetings** for users
- 📊 User database and statistics
- 🌐 **Built-in web server** for Render compatibility
- 🔒 Secure - no credentials in code

## 🎮 Commands

### For Owner:
- `/start` - View dashboard and stats
- `/broadcast <message>` - Send message to all users
- `/stats` - View bot statistics

### For Users:
- `/start` - Start the bot and see menu buttons
- Send any message to contact Sam

## 🌟 User Experience

Users get:
- Random engaging greetings when they message
- Quick access buttons (Join Channel, Contact Admin)
- Fast responses from Sam

## 🔧 Environment Variables Required

Set these on Render:

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Your bot token from @BotFather | `123456:ABC-DEF...` |
| `OWNER_ID` | Your Telegram user ID | `8242974141` |
| `JOIN_LINK_1` | Your WhatsApp/Telegram channel link | `https://whatsapp.com/channel/...` |
| `ADMIN_LINK` | Your Telegram profile link | `https://t.me/fr_sammm11` |
| `PORT` | Port for web server (auto-set by Render) | `10000` |

## 🚀 Deploy on Render

1. Create a new **Web Service** on Render
2. Connect your GitHub repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: Free
4. Add all environment variables
5. Deploy!

## ⚡ Why It Works on Render Free Tier

This bot includes a built-in web server that responds to Render's health checks, preventing timeouts. The bot stays online 24/7 on the free tier!

## 📱 How It Works

1. **Users** send messages → Bot forwards to owner with details
2. **Owner** replies to forwarded messages → Bot sends reply to user
3. **Broadcast** feature sends messages to all users at once
4. **Buttons** provide quick access to channels and admin contact
5. **Web server** keeps Render happy with health checks

## 🎯 Greetings

Users receive random fun greetings like:
- "✨ Got it! Sam will reply soon!"
- "�� Your message just landed! Sam will reply!"
- "💫 Delivered successfully! Stay tuned!"

## 🔒 Security

⚠️ **NEVER** commit credentials to the repository. Always use environment variables.

## 📊 Statistics

Track:
- Total users
- Active conversations
- Broadcast reach

## 🛠️ Troubleshooting

If bot stops working:
1. Check Render logs
2. Verify all environment variables are set
3. Ensure PORT is set (usually auto-set by Render)
4. Check bot token is valid

## 🆓 Free Tier Notes

- Render free tier may spin down after 15 minutes of inactivity
- First request after spin-down takes 50+ seconds
- The web server keeps it active and responding to health checks

## 🛠️ Support

For issues or questions, open an issue in this repository.

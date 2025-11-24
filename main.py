import os
import json
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

class URLEncoder:
    def __init__(self):
        self.config_file = "url_encoder_config.json"
        self.admin_id = 1354754957
        self.default_token = "8579629908:AAEzfmcMot6MUiDd6tfxXw0xYDVNUHws8i8"
        
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {'bot_token': self.default_token}
    
    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def encode_text(self, text):
        return urllib.parse.quote(text, safe='')
    
    def create_url(self, username, text):
        clean_name = username.lstrip('@')
        encoded_text = self.encode_text(text)
        return f"https://t.me/{clean_name}?text={encoded_text}"

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    encoder = URLEncoder()
    error_msg = f"```\n{context.error}\n```"
    try:
        await context.bot.send_message(
            chat_id=encoder.admin_id,
            text=f"🚨 *Bot Error* 🚨\n\n{error_msg}",
            parse_mode='Markdown'
        )
    except:
        pass

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Encode URL", callback_data="encode_url")],
        [InlineKeyboardButton("🤔 WTF Is This", callback_data="what_the_fuck")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """🔗 *URL ENCODER*

I turn your messages into Telegram share URLs instantly!

How it works:
1. Choose a username
2. Type your message  
3. Get your encoded URL

Let's encode some URLs! 🚀"""
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "encode_url":
        keyboard = [
            [InlineKeyboardButton("😎 Use My Username", callback_data="use_my_username")],
            [InlineKeyboardButton("⌨️ Type Username", callback_data="type_username")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Choose username source:", reply_markup=reply_markup)
        
    elif query.data == "use_my_username":
        user = query.from_user
        username = user.username or f"id{user.id}"
        context.user_data['target_username'] = username
        
        await query.edit_message_text(
            f"✅ Using: @{username}\n\nNow send me the message you want to encode:"
        )
        context.user_data['awaiting_message'] = True
        
    elif query.data == "type_username":
        await query.edit_message_text(
            "Send me the username (with or without @):"
        )
        context.user_data['awaiting_username'] = True
        
    elif query.data == "what_the_fuck":
        about_text = """🔥 *WHAT IN THE HEAVEN IS THIS?*

It's a telegram TG premium feature and I'm giving it for free!

I made this because I was tired of manually encoding URLs like some peasant and don't wanna buy subscription just for this.
Now you can be lazy like me and let the bot do the fucking work.

> "The best code is the code you don't have to write twice."
> - Reinhart probably

*The Developer:*
[Reinhart](https://t.me/kiri0507) | [Instagram](https://www.instagram.com/reinhart.dev?igsh=MWF3aWhsNWtpM2N5bQ==)

*My Bullshit Philosophy:*
- If it compiles, ship it
- If it works, don't touch it  
- If it breaks, it's someone else's problem
- If users complain, tell them it's a feature

This code probably has more bugs than features, but it works... mostly.

*Sample URL:* [Test it here!](https://t.me/kiri0507?text=i%20like%20your%20url%20encoder%20telegram%20bot%20%2C%20i%20really%20appreciate%20it)"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(about_text, reply_markup=reply_markup, parse_mode='Markdown', disable_web_page_preview=False)
        
    elif query.data == "back_main":
        keyboard = [
            [InlineKeyboardButton("🚀 Encode URL", callback_data="encode_url")],
            [InlineKeyboardButton("🤔 WTF Is This", callback_data="what_the_fuck")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Main menu - ready to encode some URLs?", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    encoder = URLEncoder()
    
    if context.user_data.get('awaiting_username'):
        username = user_message.lstrip('@').strip()
        if not username:
            await update.message.reply_text("Invalid username. Try again:")
            return
            
        context.user_data['target_username'] = username
        context.user_data['awaiting_username'] = False
        context.user_data['awaiting_message'] = True
        
        await update.message.reply_text(f"✅ Target: @{username}\n\nNow send me the message to encode:")
        
    elif context.user_data.get('awaiting_message'):
        username = context.user_data.get('target_username')
        if not username:
            await update.message.reply_text("Something went wrong. Start over with /start")
            return
            
        encoded_url = encoder.create_url(username, user_message)
        
        result_text = f"""🎉 *URL READY!*

*Target:* @{username}
*Message:* {user_message}

*Encoded URL:*
`{encoded_url}`

[Tap here to test it!]({encoded_url})"""

        keyboard = [
            [InlineKeyboardButton("🔄 New URL", callback_data="encode_url")],
            [InlineKeyboardButton("📤 Share URL", url=encoded_url)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(result_text, reply_markup=reply_markup, parse_mode='Markdown', disable_web_page_preview=False)
        
        context.user_data['awaiting_message'] = False
        context.user_data['target_username'] = None
        
    else:
        keyboard = [
            [InlineKeyboardButton("🚀 Encode URL", callback_data="encode_url")],
            [InlineKeyboardButton("🤔 WTF Is This", callback_data="what_the_fuck")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Use the buttons below to get started!", reply_markup=reply_markup)

def main():
    encoder = URLEncoder()
    config = encoder.load_config()
    
    token = config.get('bot_token', encoder.default_token)
    
    print("""
    
 ██╗   ██╗██████╗ ██╗      ██████╗ ███████╗███╗   ██╗ ██████╗ ██████╗ ███████╗██████╗ 
 ██║   ██║██╔══██╗██║     ██╔═══██╗██╔════╝████╗  ██║██╔════╝ ██╔══██╗██╔════╝██╔══██╗
 ██║   ██║██████╔╝██║     ██║   ██║█████╗  ██╔██╗ ██║██║  ███╗██████╔╝█████╗  ██████╔╝
 ██║   ██║██╔══██╗██║     ██║   ██║██╔══╝  ██║╚██╗██║██║   ██║██╔══██╗██╔══╝  ██╔══██╗
 ╚██████╔╝██║  ██║███████╗╚██████╔╝███████╗██║ ╚████║╚██████╔╝██║  ██║███████╗██║  ██║
  ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                                                                                       
    """)
    print("🔗 URL ENCODER BOT")
    print("=" * 50)
    print(f"🤖 Using token: {token[:15]}...")
    print("🚀 Starting bot...")
    
    try:
        app = Application.builder().token(token).build()
        
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CallbackQueryHandler(handle_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_error_handler(error_handler)
        
        print("✅ Bot is running! Press Ctrl+C to stop.")
        app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("🔄 Removing config...")
        config.pop('bot_token', None)
        encoder.save_config(config)
        print("✅ Config cleared. Restart the bot.")

if __name__ == "__main__":
    main()

import os
import json
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

class CryptoEncoder:
    def __init__(self):
        self.config_file = "crypto_config.json"
        
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def encode_text(self, text):
        return urllib.parse.quote(text, safe='')
    
    def create_url(self, username, text):
        clean_name = username.lstrip('@')
        encoded_text = self.encode_text(text)
        return f"https://t.me/{clean_name}?text={encoded_text}"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Create URL", callback_data="create_url")],
        [InlineKeyboardButton("🤔 About", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """💎 *CRYPTO ENCODER*

I turn your messages into Telegram share URLs instantly!

How it works:
1. Choose a username
2. Type your message
3. Get your encoded URL

Let's get started!"""
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "create_url":
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
        
    elif query.data == "about":
        about_text = """🔥 *ABOUT CRYPTO*

Built during a late-night coding session fueled by caffeine and determination.

I created this because manual URL encoding is tedious. Now you can generate Telegram share links in seconds!

> "The best code is the code you don't have to write twice."
> - Reinhart probably

*The Developer:*
Name: Reinhart  
Telegram: @kiri0507  
Instagram: @reinhart.dev  

*Development Philosophy:*
- If it works, ship it
- If it breaks, fix it fast  
- If users are happy, we're doing it right

This tool just works - no complicated setup, no bullshit."""
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(about_text, reply_markup=reply_markup, parse_mode='Markdown')
        
    elif query.data == "back_main":
        keyboard = [
            [InlineKeyboardButton("🚀 Create URL", callback_data="create_url")],
            [InlineKeyboardButton("🤔 About", callback_data="about")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Main menu - ready to encode some URLs?", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    encoder = CryptoEncoder()
    
    if context.user_data.get('awaiting_username'):
        username = user_message.lstrip('@').strip()
        if not username:
            await update.message.reply_text("Invalid username. Please try again:")
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

Tap to copy or share it directly!"""

        keyboard = [
            [InlineKeyboardButton("🔄 New URL", callback_data="create_url")],
            [InlineKeyboardButton("📤 Share URL", url=encoded_url)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')
        
        context.user_data['awaiting_message'] = False
        context.user_data['target_username'] = None
        
    else:
        keyboard = [
            [InlineKeyboardButton("🚀 Create URL", callback_data="create_url")],
            [InlineKeyboardButton("🤔 About", callback_data="about")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Use the buttons below to get started!", reply_markup=reply_markup)

def main():
    encoder = CryptoEncoder()
    config = encoder.load_config()
    
    if not config.get('bot_token'):
        print("""
        
_________                        __          
\_   ___ \_____________ ___.__._/  |_  ____  
/    \  \/\_  __ \____ <   |  |\   __\/  _ \ 
\     \____|  | \/  |_> >___  | |  | (  <_> )
 \______  /|__|  |   __// ____| |__|  \____/ 
        \/       |__|   \/                   

        """)
        print("💎 CRYPTO URL ENCODER")
        print("=" * 40)
        token = input("\n🤖 Enter your bot token: ").strip()
        
        if not token:
            print("❌ No token provided")
            return
            
        config['bot_token'] = token
        encoder.save_config(config)
        print("✅ Config saved! Starting bot...")
    else:
        token = config['bot_token']
        print("🔄 Found existing config. Starting bot...")
    
    try:
        app = Application.builder().token(token).build()
        
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CallbackQueryHandler(handle_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("🤖 Bot is running! Press Ctrl+C to stop.")
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("🔄 Removing invalid config...")
        config.pop('bot_token', None)
        encoder.save_config(config)
        print("✅ Config cleared. Please restart with a valid token.")

if __name__ == "__main__":
    main()

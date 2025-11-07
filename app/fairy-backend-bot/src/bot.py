import os
import discord
from discord.ext import commands
import asyncio
import aiohttp
from dotenv import load_dotenv

import src.utils as utils

logger = utils.logger

def setup_bot():
    """Initialize Discord client with intents"""
    # Set up required intents
    intents = discord.Intents.default()
    intents.message_content = True  # Read message content
    intents.guilds = True          # Access guild information
    intents.guild_messages = True  # Receive guild messages
    
    # Create bot instance
    bot = commands.Bot(
        command_prefix='!',  # Not used for mentions, but required
        intents=intents,
        help_command=None  # Disable default help command
    )
    
    return bot

def run_bot():
    load_dotenv()

    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("DISCORD_BOT_TOKEN not found in environment variables")
        raise ValueError("DISCORD_BOT_TOKEN is required")
    
    bot = setup_bot()
    
    @bot.event
    async def on_ready():
        """Event handler for bot startup"""
        if bot.user:
            logger.info(f"Bot connected as {bot.user.name} (ID: {bot.user.id})")
        logger.info(f"Connected to {len(bot.guilds)} guilds")
        
        # Set bot status
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="ホロウを探索中..."
            )
        )
        
        logger.info("Fairyの起動が完了しました。")
    
    @bot.event
    async def on_message(message):
        # 自分のメッセージで連鎖反応を起こすのを防止
        if message.author == bot.user:
            return

        # メンション検出
        if bot.user and bot.user.mentioned_in(message):
            content = message.content
            for mention in message.mentions:
                if mention == bot.user:
                    content = content.replace(f'<@{mention.id}>', '').strip()
            
            if content:
                async with message.channel.typing():
                    try:
                        # Get JWT token first
                        async with aiohttp.ClientSession() as session:
                            async with session.post(
                                f"{os.getenv('BACKEND_API_URL')}/api/auth/token",
                                params={'user_id': message.author.id}
                            ) as token_response:
                                if token_response.status != 200:
                                    await message.reply("マスター、認証に失敗しました。")
                                    return
                                token_data = await token_response.json()
                                access_token = token_data['access_token']
                            
                            # POST to FastAPI /research endpoint with JWT
                            headers = {'Authorization': f'Bearer {access_token}'}
                            async with session.post(
                                f"{os.getenv('BACKEND_API_URL')}/api/research",
                                json={'user_id': message.author.id, 'keyword': content},
                                headers=headers
                            ) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    owner_mention = f"<@{result['owner']}>"
                                    reply_text = f"{owner_mention}\n{result['smart_message']}"
                                    reply_text += f"""\n\nマスター、以下のインターノットリンクに詳細情報をまとめました。必要でしたらご確認ください。
                                                        \nURL：https://fairy.krz-tech.net/{result['uuid']}
                                                        \nFairy処理時間：{result['time']}秒"""
                                    await message.reply(reply_text)
                                else:
                                    await message.reply("マスター、探索中にエラーが発生しました。")
                    except Exception as e:
                        logger.error(f"Research request failed: {e}")
                        await message.reply("マスター、探索中にエラーが発生しました。管理者に確認してみてください。")
    
    # Run the bot
    try:
        logger.info("Starting bot...")
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Invalid bot token provided")
        raise
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise
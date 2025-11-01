import os
import discord
from discord.ext import commands
import asyncio
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
                type=discord.ActivityType.listening,
                name="Zenless Zone Zero"
            )
        )
        
        logger.info("Fairyの起動が完了しました。")
    
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
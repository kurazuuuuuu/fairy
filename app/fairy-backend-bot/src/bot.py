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

class ToSView(discord.ui.View):
    def __init__(self, user_id: int, access_token: str):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.access_token = access_token

    @discord.ui.button(label="利用規約に同意する", style=discord.ButtonStyle.green)
    async def agree_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("これはあなたのためのボタンではありません。", ephemeral=True)
            return

        await interaction.response.defer()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.access_token}'}
                async with session.post(
                    f"{os.getenv('BACKEND_API_URL')}/api/users/tos",
                    json={'user_id': self.user_id},
                    headers=headers
                ) as response:
                    if response.status == 200:
                        await interaction.message.edit(
                            content="マスター、利用規約への同意を確認しました。これよりFairyの全機能をご利用いただけます。\n\nお手数ですが、もう一度リクエストを送信してください。",
                            view=None
                        )
                        self.stop()
                    else:
                        await interaction.followup.send("マスター、同意の処理中にエラーが発生しました。", ephemeral=True)
        except Exception as e:
            logger.error(f"ToS agreement failed: {e}")
            await interaction.followup.send("マスター、通信エラーが発生しました。", ephemeral=True)

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
                                json={'user_id': message.author.id}
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
                                elif response.status == 403:
                                    # ToS not agreed
                                    view = ToSView(message.author.id, access_token)
                                    await message.reply(
                                        "マスター、Fairyの機能を使用するには、以下の利用規約に同意する必要があります。\n\n"
                                        "1. **Gemini APIの利用**: 情報収集・分析のためにGoogle Gemini APIを使用します。\n"
                                        "2. **データの保存**: リサーチ結果や会話データは、サービスの品質向上および履歴管理のために保存されます。\n"
                                        "3. **免責事項**: 生成された情報の正確性について保証するものではありません。\n\n"
                                        "同意いただける場合は、下のボタンを押してください。",
                                        view=view
                                    )
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
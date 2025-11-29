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

        await interaction.response.defer(ephemeral=True)
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.access_token}'}
                async with session.post(
                    f"{os.getenv('BACKEND_API_URL')}/api/users/tos",
                    json={'user_id': self.user_id},
                    headers=headers
                ) as response:
                    if response.status == 200:
                        await interaction.followup.send(
                            "マスター、利用規約への同意を確認しました。これよりFairyの全機能をご利用いただけます。\n\nお手数ですが、もう一度元のチャンネルでリクエストを送信してください。",
                            ephemeral=True
                        )
                        try:
                            await interaction.message.delete()
                        except discord.NotFound:
                            pass
                        self.stop()
                    else:
                        await interaction.followup.send("マスター、同意の処理中にエラーが発生しました。管理者に連絡してください。", ephemeral=True)
        except Exception as e:
            logger.error(f"ToS agreement failed: {e}")
            await interaction.followup.send("マスター、通信エラーが発生しました。管理者に連絡してください。", ephemeral=True)

async def send_tos_request(message, user_id, access_token):
    view = ToSView(user_id, access_token)
    
    embed = ToS()
    embed.set_footer(text="同意いただける場合は、下のボタンを押してください。")

    try:
        # DM送信
        await message.author.send(embed=embed, view=view)
        # DM送信通知
        await message.reply("マスター、Fairyの利用規約をDMに送信しました。ご確認ください。", delete_after=10)
    except discord.Forbidden:
        # ユーザー設定によりDMが送信できなかった場合の対応
        await message.reply(
            "マスター、DMを送信できませんでした。設定をご確認ください。こちらで同意していただくことも可能です。",
            embed=embed,
            view=view,
            delete_after=30
        )

async def ToS():
    embed = discord.Embed(
        title="利用規約への同意",
        description="マスター、Fairyの機能を使用するには、以下の利用規約に同意する必要があります。",
        color=0x00b0f4
    )
    embed.add_field(
        name="1. Gemini APIの利用",
        value="情報収集・分析のためにGoogle Gemini APIを使用します。",
        inline=False
    )
    embed.add_field(
        name="2. データの保存",
        value="リサーチ結果や会話データは、サービスの品質向上および履歴管理のために保存されます。",
        inline=False
    )
    embed.add_field(
        name="3. 免責事項",
        value="生成された情報の正確性について保証するものではありません。",
        inline=False
    )
    return embed

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
                name="ホロウをホロウ..."
            )
        )
        
        logger.info("Fairyの起動が完了しました。")
    
    @bot.event
    async def on_message(message):
        # 自分のメッセージで連鎖反応を起こすのを防止
        if message.author == bot.user:
            return

        # メンション検出または返信検出
        is_mention = bot.user and bot.user.mentioned_in(message)
        is_reply = message.reference is not None

        if is_mention or is_reply:
            content = message.content
            # メンション部分を削除
            if bot.user:
                for mention in message.mentions:
                    if mention == bot.user:
                        content = content.replace(f'<@{mention.id}>', '').strip()
            
            # リプライの場合、リサーチ結果への返信かチェック
            if is_reply and not is_mention:
                try:
                    ref_msg = await message.channel.fetch_message(message.reference.message_id)
                    # Bot自身のメッセージかつ、リサーチ結果URLが含まれているか確認
                    is_research_result = (
                        ref_msg.author == bot.user and 
                        "https://fairy.krz-tech.net/" in ref_msg.content
                    )
                    if not is_research_result:
                        return
                except discord.NotFound:
                    return
                except Exception as e:
                    logger.error(f"Failed to fetch referenced message: {e}")
                    return

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
                            
                            headers = {'Authorization': f'Bearer {access_token}'}
                            
                            # Determine if this is a follow-up or new research
                            if is_reply and message.reference.message_id:
                                # Follow-up Research
                                parent_message_id = message.reference.message_id
                                # Check if parent message is from bot (optional, but good practice)
                                # For now, we assume if it's a reply to bot (or just a reply where bot is mentioned/active), we try follow-up
                                
                                async with session.post(
                                    f"{os.getenv('BACKEND_API_URL')}/api/research/followup",
                                    json={
                                        'user_id': message.author.id, 
                                        'keyword': content,
                                        'parent_message_id': parent_message_id
                                    },
                                    headers=headers
                                ) as response:
                                    if response.status == 200:
                                        result = await response.json()
                                        await send_research_result(message, result, session, headers)
                                    elif response.status == 404:
                                        # Parent research not found, maybe treat as new research?
                                        await message.reply("マスター、元のリサーチ結果が見つかりませんでした。新規リサーチとして承りますか？")
                                    elif response.status == 403:
                                         await send_tos_request(message, message.author.id, access_token)
                                    else:
                                        await message.reply("マスター、追加ホロウ探索にエラーが発生しました。")
                            else:
                                # New Research
                                async with session.post(
                                    f"{os.getenv('BACKEND_API_URL')}/api/research",
                                    json={'user_id': message.author.id, 'keyword': content},
                                    headers=headers
                                ) as response:
                                    if response.status == 200:
                                        result = await response.json()
                                        await send_research_result(message, result, session, headers)
                                    elif response.status == 403:
                                        await send_tos_request(message, message.author.id, access_token)
                                    else:
                                        await message.reply("マスター、ホロウ探索中にエラーが発生しました。")
                    except Exception as e:
                        logger.error(f"Research request failed: {e}")
                        await message.reply("マスター、ホロウ探索中に問題が発生しました。管理者に確認してみてください。")

    async def send_research_result(message, result, session, headers):
        owner_mention = f"<@{result['owner']}>"
        reply_text = f"{owner_mention}\n{result['smart_message']}"
        reply_text += f"""\n\nマスター、以下のインターノットリンクに詳細情報をまとめました。必要でしたらご確認ください。
                            \nURL：https://fairy.krz-tech.net/{result['uuid']}
                            \n{result['time']} sec || {result.get('total_tokens', 'N/A')} Token"""
        sent_message = await message.reply(reply_text)
        
        # Update message_id in backend
        try:
            async with session.patch(
                f"{os.getenv('BACKEND_API_URL')}/api/research/{result['uuid']}/message",
                json={'message_id': sent_message.id},
                headers=headers
            ) as patch_response:
                if patch_response.status != 200:
                    logger.warning(f"Failed to update message_id for research {result['uuid']}")
        except Exception as e:
            logger.error(f"Failed to update message_id: {e}")

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
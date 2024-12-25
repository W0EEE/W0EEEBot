import discord
import logging
from discord import app_commands
from commands import commands
from db.uls import UlsClient
import asyncpg as pg
from db.qrz import QrzClient

logger = logging.getLogger("W0EEEBot")

class W0eeeBot(discord.Client):
    version: str
    def __init__(self, bot_db_url: str, uls_db_url: str, listening_to: str | None, qrz_user: str | None, qrz_pass: str | None, version: str):        
        super().__init__(intents=discord.Intents.default())
        
        self.bot_db_url = bot_db_url
        self.uls_db_url = uls_db_url
        self.listening_to = listening_to
        self.version = version
        
        root = app_commands.CommandTree(self)
        self.tree = root
        
        if qrz_user is not None and qrz_pass is not None:
            self.qrz = QrzClient(qrz_user, qrz_pass, QrzClient.compose_agent("W0EEEBot", version))
        else:
            self.qrz = None
        
        @root.command()
        async def ping(interaction: discord.Interaction):
            """hey w0eeebot... you alive?"""
            await interaction.response.send_message(f"""Pong!
W0EEEBot {self.version} :)""")
        
        for cmd in commands.values():
            root.add_command(cmd.tree())
        
    async def on_ready(self):
        self.uls = UlsClient(await pg.create_pool(self.uls_db_url))
        #self.botpool = await pg.create_pool(self.bot_db_url)
        
        if self.qrz is not None:
            await self.qrz._renew_token()
        
        if self.listening_to is not None:
            activity = discord.Activity(name=self.listening_to)
            activity.type = discord.ActivityType.listening
            
            await self.change_presence(activity=activity)
        
        logger.info(f'Logged on as {self.user}')
    
    async def setup_hook(self):
        await self.tree.sync()
        logger.info('Synced application commands')

import discord
import logging
from discord import app_commands
from commands import commands
from db.uls import UlsClient
import asyncpg as pg

logger = logging.getLogger("W0EEEBot")

class W0eeeBot(discord.Client):
    version: str
    def __init__(self, bot_db_url: str, uls_db_url: str, listening_to: str | None, version: str):        
        super().__init__(intents=discord.Intents.default())
        
        self.bot_db_url = bot_db_url
        self.uls_db_url = uls_db_url
        self.listening_to = listening_to
        self.version = version
        
        root = app_commands.CommandTree(self)
        self.tree = root
        
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
        
        if self.listening_to is not None:
            activity = discord.Activity(name=self.listening_to)
            activity.type = discord.ActivityType.listening
            
            await self.change_presence(activity=activity)
        
        logger.info(f'Logged on as {self.user}')
    
    async def setup_hook(self):
        await self.tree.sync()
        logger.info('Synced application commands')

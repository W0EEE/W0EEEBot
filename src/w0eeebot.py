import discord
import logging
from discord import app_commands
from commands import commands
from db.uls import UlsClient
import asyncpg as pg

W0EEEBOT_VERSION = '3.0.0'

logger = logging.getLogger("W0EEEBot")

class W0eeeBot(discord.Client):
    def __init__(self, bot_db_url: str, uls_db_url: str):        
        super().__init__(intents=discord.Intents.default())
        
        self.bot_db_url = bot_db_url
        self.uls_db_url = uls_db_url
        
        root = app_commands.CommandTree(self)
        self.tree = root
        
        @root.command()
        async def ping(interaction: discord.Interaction):
            """hey w0eeebot... you alive?"""
            await interaction.response.send_message(f"""Pong!
W0EEEBot {self.version()} :)""")
        
        for cmd in commands.values():
            root.add_command(cmd.tree())
        
    async def on_ready(self):
        self.uls = UlsClient(await pg.create_pool(self.uls_db_url))
        #self.botpool = await pg.create_pool(self.bot_db_url)
        
        logger.info(f'Logged on as {self.user}')
    
    async def setup_hook(self):
        await self.tree.sync()
        logger.info('Synced application commands')
        
    def version(self = None) -> str:
        return W0EEEBOT_VERSION

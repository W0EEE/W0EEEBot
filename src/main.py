# This file is just a simple wrapper around the W0eeeBot class
# It mostly just loads the configuration from the environment and instantiates the class

import os
import sys
import logging
from dotenv import load_dotenv
from w0eeebot import W0eeeBot

logger = logging.getLogger('main')

def main() -> int | None:
    required_envvars = {
        'DISCORD_BOT_TOKEN': 'Discord bot token',
        'BOT_DB_URL': 'Postgres URL to access bot database',
        'ULS_DB_URL': 'Postgres URL to access ULS database'
    }
    
    for var, description in required_envvars.items():
        if var not in os.environ:
            logger.error(f"Environment variable {var} missing.")
            logger.error(f"Must provide {description}.")
            return 1

    bot = W0eeeBot(os.environ['BOT_DB_URL'], os.environ['ULS_DB_URL'])
    bot.run(os.environ['DISCORD_BOT_TOKEN'], root_logger=True)
    
if __name__ == '__main__':
    load_dotenv()
    status = main()
    if status:
        sys.exit(status)
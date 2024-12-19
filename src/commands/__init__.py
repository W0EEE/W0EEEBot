import os
import importlib

commands = {}

for filename in os.listdir(os.path.dirname(__file__)):
    if not filename.endswith('.py') or filename.startswith('_'):
        continue
    
    # remove the file extension and export
    module_name = filename[:-3]
    module = importlib.import_module(f"commands.{module_name}")
    commands[module_name] = module

import importlib
import pkgutil
from discord import app_commands


async def load_commands(tree: app_commands.CommandTree, guild_id: int):
    from bot import commands

    for module_info in pkgutil.iter_modules(commands.__path__):
        if not module_info.ispkg:
            module_name = module_info.name
            module = importlib.import_module(f"bot.commands.{module_name}")
            if hasattr(module, "setup"):
                await module.setup(tree, guild_id)
                print(f"Loaded command module: {module_name}")

"""
Bot Discord Draman - Point d'entrée principal
Bot de modération Discord avec système de laisse et protection ultime
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Ajouter le dossier courant au Python path pour Render
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import discord
from discord.ext import commands

from config import Config
from database.manager import DatabaseManager
from keep_alive import start_keep_alive

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DramanBot(commands.Bot):
    """Bot principal Draman avec gestion de base de données et cogs"""
    
    def __init__(self):
        # Configuration des intents Discord
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.voice_states = True
        intents.guilds = True
        intents.moderation = True
        
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        self.db_manager = None
        self.config = Config
        
    async def setup_hook(self):
        """Configuration initiale du bot"""
        logger.info("🚀 Démarrage du bot Draman...")
        
        # Validation de la configuration
        if not Config.validate():
            logger.error("❌ Configuration invalide")
            await self.close()
            return
        
        # Initialisation de la base de données
        try:
            self.db_manager = DatabaseManager()
            await self.db_manager.initialize()
            logger.info("✅ Base de données initialisée avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation base de données: {e}")
            raise
        
        # Chargement des cogs
        cogs_to_load = [
            'cogs.moderation',
            'cogs.protection', 
            'cogs.leash',
            'events.member_handler',
            'events.voice_handler'
        ]
        
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ Cog chargé: {cog}")
            except Exception as e:
                logger.error(f"❌ Erreur chargement cog {cog}: {e}")
                # Ne pas arrêter le bot pour un cog défaillant
                continue
        
        # Synchronisation des commandes slash
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ {len(synced)} commandes slash synchronisées")
        except Exception as e:
            logger.error(f"❌ Erreur synchronisation commandes: {e}")
    
    async def on_ready(self):
        """Événement déclenché quand le bot est prêt"""
        if self.user:
            logger.info(f"🤖 {self.user} est connecté et prêt!")
            logger.info(f"🔢 Bot ID: {self.user.id}")
        else:
            logger.error("❌ Erreur: self.user est None")
        logger.info(f"🏠 Connecté à {len(self.guilds)} serveur(s)")
        
        # Affichage des serveurs
        for guild in self.guilds:
            if guild:
                logger.info(f"  - {guild.name} (ID: {guild.id})")
        
        # Statut du bot
        try:
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="🐕‍🦺 le système de laisse"
                ),
                status=discord.Status.online
            )
        except Exception as e:
            logger.error(f"❌ Erreur définition du statut: {e}")
    
    async def on_command_error(self, ctx, error):
        """Gestion globale des erreurs de commandes"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Vous n'avez pas les permissions nécessaires.")
            return
        
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Je n'ai pas les permissions nécessaires.")
            return
        
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Membre non trouvé.")
            return
        
        logger.error(f"Erreur commande {ctx.command}: {error}", exc_info=True)
        try:
            await ctx.send(f"❌ Erreur inattendue: {str(error)[:100]}...")
        except:
            pass
    
    async def close(self):
        """Nettoyage lors de la fermeture du bot"""
        logger.info("🔄 Fermeture du bot...")
        
        if self.db_manager:
            await self.db_manager.close()
            logger.info("✅ Base de données fermée")
        
        await super().close()

async def main():
    """Fonction principale"""
    # Vérification de la configuration
    if not Config.validate():
        logger.error("❌ Configuration invalide")
        sys.exit(1)
    
    # Démarrage du serveur keep-alive si configuré
    if Config.KEEP_ALIVE:
        logger.info("🌐 Démarrage du serveur keep-alive...")
        start_keep_alive()
    
    # Création et démarrage du bot
    bot = DramanBot()
    
    try:
        await bot.start(Config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur critique: {e}", exc_info=True)
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot arrêté")
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}", exc_info=True)
        sys.exit(1)

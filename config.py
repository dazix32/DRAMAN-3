"""
Configuration centralisée pour le bot Discord Draman
"""

import os
from typing import List

class Config:
    """Configuration principale du bot"""
    
    # Token Discord (OBLIGATOIRE)
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    
    # IDs Discord importants
    BOSS_ULTIMATE_ID: int = int(os.getenv("BOSS_ULTIMATE_ID", "0"))
    MAIN_GUILD_ID: int = int(os.getenv("MAIN_GUILD_ID", "0"))
    
    # Configuration du bot
    COMMAND_PREFIX: str = os.getenv("COMMAND_PREFIX", "!")
    
    # Configuration de la base de données
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "bot_database.db")
    
    # Configuration du serveur web (keep-alive)
    PORT: int = int(os.getenv("PORT", "5000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Configuration Render
    RENDER: bool = os.getenv("RENDER", "false").lower() == "true"
    KEEP_ALIVE: bool = os.getenv("KEEP_ALIVE", "true").lower() == "true"
    
    # Configuration des logs
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Permissions par défaut
    MODERATOR_ROLES: List[str] = [
        "Modérateur", "Moderator", "Mod", 
        "Administrateur", "Administrator", "Admin"
    ]
    
    ADMIN_ROLES: List[str] = [
        "Administrateur", "Administrator", "Admin", "Owner"
    ]
    
    # Configuration des sanctions
    MAX_WARNINGS: int = int(os.getenv("MAX_WARNINGS", "3"))
    WAKEUP_MOVES: int = int(os.getenv("WAKEUP_MOVES", "15"))
    
    # Configuration du système de laisse
    LEASH_COOLDOWN: int = int(os.getenv("LEASH_COOLDOWN", "5"))  # secondes
    DOG_NICKNAME_PREFIX: str = "🐕‍🦺 de "
    
    # Messages d'erreur personnalisés
    MESSAGES = {
        "no_permission": "❌ Vous n'avez pas la permission d'utiliser cette commande.",
        "bot_no_permission": "❌ Je n'ai pas les permissions nécessaires pour effectuer cette action.",
        "user_not_found": "❌ Utilisateur non trouvé.",
        "hierarchy_error": "❌ Vous ne pouvez pas effectuer cette action sur cet utilisateur (hiérarchie).",
        "boss_protected": "🛡️ Le boss ultime est protégé et ne peut pas être sanctionné.",
        "self_action": "❌ Vous ne pouvez pas effectuer cette action sur vous-même.",
        "bot_action": "❌ Je ne peux pas effectuer cette action sur un autre bot.",
        "already_sanctioned": "⚠️ Cet utilisateur est déjà sanctionné.",
        "not_sanctioned": "⚠️ Cet utilisateur n'est pas sanctionné.",
        "database_error": "❌ Erreur de base de données. Veuillez réessayer.",
        "success": "✅ Action effectuée avec succès."
    }
    
    @classmethod
    def validate(cls) -> bool:
        """Valide la configuration"""
        errors = []
        
        if not cls.DISCORD_TOKEN:
            errors.append("DISCORD_TOKEN est requis")
        
        if cls.BOSS_ULTIMATE_ID == 0:
            errors.append("BOSS_ULTIMATE_ID est requis")
        
        if cls.MAIN_GUILD_ID == 0:
            errors.append("MAIN_GUILD_ID est requis")
        
        if errors:
            print("❌ Erreurs de configuration:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def get_permission_level(cls, member) -> int:
        """
        Retourne le niveau de permission d'un membre
        0: Utilisateur normal
        1: Modérateur
        2: Administrateur  
        3: Boss ultime
        """
        if member.id == cls.BOSS_ULTIMATE_ID:
            return 3
        
        if member.guild_permissions.administrator:
            return 2
        
        # Vérification des rôles admin
        for role in member.roles:
            if role.name in cls.ADMIN_ROLES:
                return 2
        
        # Vérification des rôles modérateur
        for role in member.roles:
            if role.name in cls.MODERATOR_ROLES:
                return 1
        
        return 0
    
    @classmethod
    def is_boss(cls, user_id: int) -> bool:
        """Vérifie si l'utilisateur est le boss ultime"""
        return user_id == cls.BOSS_ULTIMATE_ID
    
    @classmethod
    def is_moderator(cls, member) -> bool:
        """Vérifie si le membre est modérateur ou plus"""
        return cls.get_permission_level(member) >= 1
    
    @classmethod
    def is_admin(cls, member) -> bool:
        """Vérifie si le membre est administrateur ou plus"""
        return cls.get_permission_level(member) >= 2

#!/usr/bin/env python3
"""
Script de test pour vérifier que tous les modules peuvent être importés
"""

import sys
import os

def test_imports():
    """Test tous les imports du bot"""
    print("🧪 Test des imports...")
    
    try:
        # Test import config
        from config import Config
        print("✅ Config importé")
        
        # Test import database
        from database.manager import DatabaseManager
        print("✅ DatabaseManager importé")
        
        # Test import keep_alive
        from keep_alive import KeepAliveServer
        print("✅ KeepAliveServer importé")
        
        # Test imports cogs
        print("🔧 Test des cogs...")
        sys.path.insert(0, os.getcwd())
        
        # Test basic discord import
        import discord
        from discord.ext import commands
        print("✅ Discord.py importé")
        
        print("\n🎉 TOUS LES IMPORTS FONCTIONNENT !")
        print("✅ Le bot est prêt pour le déploiement sur Render")
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test la configuration"""
    print("\n🔧 Test de la configuration...")
    
    try:
        from config import Config
        
        # Test des messages
        assert "no_permission" in Config.MESSAGES
        assert "boss_protected" in Config.MESSAGES
        print("✅ Messages de configuration OK")
        
        # Test des méthodes
        assert hasattr(Config, 'validate')
        assert hasattr(Config, 'is_boss')
        print("✅ Méthodes de configuration OK")
        
        return True
    except Exception as e:
        print(f"❌ Erreur config: {e}")
        return False

def test_database_models():
    """Test les modèles de base de données"""
    print("\n🗄️ Test des modèles de base de données...")
    
    try:
        from database.manager import Warning, ModerationLog, LeashRelation
        
        # Test création d'un warning
        from datetime import datetime
        warning = Warning(1, 123, 456, 789, "test", datetime.now(), True)
        print(f"✅ Warning créé: {warning.reason}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur modèles: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DRAMAN BOT - TESTS DE DÉPLOIEMENT")
    print("=" * 50)
    
    success = True
    
    success &= test_imports()
    success &= test_config()
    success &= test_database_models()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ Bot prêt pour Render")
        print("\n📋 INSTRUCTIONS RENDER:")
        print("1. Build Command: pip install --upgrade pip && pip install -r requirements.txt")
        print("2. Start Command: python main.py")
        print("3. Variables: DISCORD_TOKEN, BOSS_ULTIMATE_ID, MAIN_GUILD_ID")
        sys.exit(0)
    else:
        print("❌ ÉCHEC DES TESTS")
        print("Veuillez corriger les erreurs avant le déploiement")
        sys.exit(1)
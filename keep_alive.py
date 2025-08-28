"""
Serveur web keep-alive pour maintenir le bot actif sur Render
"""

import asyncio
import logging
import threading
import time
from datetime import datetime
from aiohttp import web

from config import Config

logger = logging.getLogger(__name__)

class KeepAliveServer:
    """Serveur web pour maintenir le bot actif"""
    
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.start_time = datetime.now()
        
    def setup_routes(self):
        """Configuration des routes"""
        self.app.router.add_get('/', self.health_check)
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/status', self.status)
        self.app.router.add_get('/ping', self.ping)
        
    async def health_check(self, request):
        """Point de santé basique"""
        return web.json_response({
            "status": "healthy",
            "service": "Draman Discord Bot",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
        })
    
    async def status(self, request):
        """Statut détaillé du service"""
        uptime = datetime.now() - self.start_time
        
        return web.json_response({
            "service": "Draman Discord Bot",
            "status": "running",
            "start_time": self.start_time.isoformat(),
            "uptime": {
                "seconds": uptime.total_seconds(),
                "formatted": str(uptime)
            },
            "config": {
                "render": Config.RENDER,
                "keep_alive": Config.KEEP_ALIVE,
                "port": Config.PORT,
                "host": Config.HOST
            },
            "endpoints": [
                "/",
                "/health", 
                "/status",
                "/ping"
            ]
        })
    
    async def ping(self, request):
        """Point de ping simple"""
        return web.Response(text="pong")
    
    async def start_server(self):
        """Démarre le serveur web"""
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, Config.HOST, Config.PORT)
            await site.start()
            
            logger.info(f"🌐 Serveur keep-alive démarré sur {Config.HOST}:{Config.PORT}")
            
            # Maintenir le serveur en vie
            while True:
                await asyncio.sleep(3600)  # 1 heure
                
        except Exception as e:
            logger.error(f"❌ Erreur serveur keep-alive: {e}")

def start_keep_alive():
    """Démarre le serveur keep-alive dans un thread séparé"""
    
    def run_server():
        """Fonction pour exécuter le serveur dans un thread"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            server = KeepAliveServer()
            loop.run_until_complete(server.start_server())
        except Exception as e:
            logger.error(f"❌ Erreur thread keep-alive: {e}")
        finally:
            try:
                loop.close()
            except:
                pass
    
    # Démarrage du serveur dans un thread séparé
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    logger.info("🚀 Thread keep-alive démarré")

def ping_self():
    """Ping périodique pour éviter l'hibernation"""
    try:
        import requests
    except ImportError:
        logger.warning("⚠️ Module requests non disponible pour self-ping")
        return
    
    def ping_loop():
        while True:
            try:
                time.sleep(25 * 60)  # 25 minutes
                
                url = f"http://127.0.0.1:{Config.PORT}/ping"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    logger.info("🏓 Self-ping réussi")
                else:
                    logger.warning(f"⚠️ Self-ping échoué: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Erreur self-ping: {e}")
    
    # Auto-ping seulement sur Render
    if Config.RENDER and Config.KEEP_ALIVE:
        ping_thread = threading.Thread(target=ping_loop, daemon=True)
        ping_thread.start()
        logger.info("🔄 Auto-ping démarré")

# Démarrage automatique si le module est importé et configuré
if Config.KEEP_ALIVE:
    ping_self()

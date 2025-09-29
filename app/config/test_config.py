from app.config.settings import get_settings

try:
    settings = get_settings()
    print("✅ Settings loaded successfully!")
    print(f"Environment: {settings.environment}")
    print(f"LiveKit WS URL: {settings.livekit_ws_url}")
    print(f"Trusted hosts: {settings.get_trusted_hosts_list()}")
    print(f"CORS origins: {settings.get_cors_origins_list()}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
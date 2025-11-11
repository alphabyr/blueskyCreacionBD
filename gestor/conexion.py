import os
from atproto import Client

class ConexionBluesky:
    """
    Clase para gestionar la conexión y autenticación con la API de Bluesky.
    Se encarga de crear y mantener una instancia autenticada de Client.
    """
    def __init__(self, handle=None, app_password=None):
        self.handle = handle or os.environ.get('BSKY_HANDLE')
        self.app_password = app_password or os.environ.get('BSKY_APP_PASSWORD')
        self.client = None
        self.logged_in = False

    def conectar(self):
        if not self.handle or not self.app_password:
            raise ValueError("Configura BSKY_HANDLE y BSKY_APP_PASSWORD.")
        self.client = Client()
        try:
            self.client.login(self.handle, self.app_password)
            self.logged_in = True
            print(f"Inicio de sesión exitoso como {self.client.me.handle}")
        except Exception as e:
            self.logged_in = False
            raise RuntimeError(f"Error al iniciar sesión: {e}")

    def get_client(self):
        if not self.logged_in or self.client is None:
            self.conectar()
        return self.client

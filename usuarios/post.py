import os
import sys
import json
import time
from pathlib import Path

# Agregar ruta del proyecto para imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gestor.conexion import ConexionBluesky
from configuracion.load_config import config
from seguridad.secure_file_handler import SecureFileHandler

class BlueskyPostsFetcher:
    """
    Clase para extraer posts de usuarios de Bluesky.

    Esta clase se conecta a Bluesky, lee perfiles de usuarios desde un archivo JSON 
    (generado previamente con la clase datosUsuario), extrae sus posts y los guarda 
    en un archivo JSON de salida. Incluye capacidad de reanudación automática.   
    

    """
    
    
    def __init__(self, handle=None, app_password=None, input_file=None, output_file=None, posts_per_user_limit=None):
        self.handle = handle or os.environ.get('BSKY_HANDLE')
        self.app_password = app_password or os.environ.get('BSKY_APP_PASSWORD')
        self.conexion = ConexionBluesky(self.handle, self.app_password)
        
        # Determinar directorio base seguro
        project_root = Path(__file__).parent.parent
        directorio_almacen = project_root / config.get('rutas', 'directorio_almacen')
        
        # Crear handler seguro para operaciones de archivos
        self.file_handler = SecureFileHandler(directorio_almacen)
        
        if input_file is None:
            input_file = config.get('rutas', 'archivo_profiles')
        
        if output_file is None:
            output_file = config.get('rutas', 'archivo_posts_json')
        
        self.input_file = input_file
        self.output_file = output_file
        self.posts_per_user_limit = posts_per_user_limit if posts_per_user_limit is not None else config.get_posts_por_usuario_limite()
        self.client = None
        self.processed_data = {}
        self.processed_dids = set()
        self.profiles_to_scan = []



    def login(self):
        """
        Inicia sesión en la cuenta Bluesky usando ConexionBluesky.
        """
        self.client = self.conexion.get_client()

    def load_progress(self):
        if self.file_handler.existe(self.output_file):
            print(f"Cargando progreso existente desde {self.output_file}...")
            try:
                with self.file_handler.abrir_lectura(self.output_file) as f:
                    self.processed_data = json.load(f)
                    self.processed_dids = set(self.processed_data.keys())
                    print(f"Progreso cargado. {len(self.processed_dids)} usuarios ya procesados.")
            except json.JSONDecodeError:
                print(f"Advertencia: {self.output_file} está corrupto. Empezando de cero.")
                self.processed_data = {}
                self.processed_dids = set()
            except ValueError as e:
                print(f"Error de seguridad: {e}")
                self.processed_data = {}
                self.processed_dids = set()
        else:
            print("No se encontró archivo de progreso. Empezando de cero.")
            self.processed_data = {}
            self.processed_dids = set()



    def load_profiles(self):
        """
        Carga los perfiles de usuarios desde el archivo JSON de entrada. Con esto se evitan duplicados.
        """
        
        try:
            with self.file_handler.abrir_lectura(self.input_file) as f:
                self.profiles_to_scan = json.load(f)
            print(f"Se cargarán {len(self.profiles_to_scan)} perfiles desde {self.input_file}.")
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: No se encontró el archivo {self.input_file}. Asegúrate de ejecutar 'fetch_profiles.py' primero.")
        except ValueError as e:
            raise ValueError(f"Error de seguridad al cargar perfiles: {e}")



    def process_profiles(self):
        """
        Procesa los perfiles cargados, obteniendo sus posts y guardando el progreso.
        """
        
        # Solo procesar los perfiles cuyo DID no esté en processed_dids
        perfiles_pendientes = [p for p in self.profiles_to_scan if p.get('did') not in self.processed_dids]
        total_profiles = len(perfiles_pendientes)
        try:
            for i, profile in enumerate(perfiles_pendientes):
                did = profile.get('did')
                handle = profile.get('handle', 'N/A')
                print(f"\n--- Procesando {i+1}/{total_profiles}: {handle} ({did}) ---")
                try:
                    response = self.client.get_author_feed(
                        actor=did,
                        limit=self.posts_per_user_limit
                    )
                    user_posts = []
                    if response.feed:
                        for feed_view in response.feed:
                            record = feed_view.post.record
                            post_data = {
                                "cid": str(feed_view.post.cid),
                                "uri": str(feed_view.post.uri),
                                "createdAt": record.created_at,
                                "text": record.text,
                                "replyCount": feed_view.post.reply_count,
                                "repostCount": feed_view.post.repost_count,
                                "likeCount": feed_view.post.like_count,
                                "hasEmbed": record.embed is not None
                            }
                            user_posts.append(post_data)
                    print(f"Se obtuvieron {len(user_posts)} posts.")
                    self.processed_data[did] = {
                        "profile": profile,
                        "posts": user_posts
                    }
                    self.save_progress()
                except Exception as e:
                    error_message = str(e)
                    if "Profile not found" in error_message or "Actor not found" in error_message:
                        print(f"⚠️ Saltando a {handle}: El usuario puede haber borrado la cuenta, cambiado de nombre o sido baneado.")
                        continue
                    elif "RateLimit" in error_message:
                        delay = config.get_delay_rate_limit()
                        print(f"⚠️ Límite de velocidad alcanzado. Esperando {delay} segundos antes de continuar.")
                        time.sleep(delay)
                    else:
                        print(f"❌ Error inesperado con {handle}: {error_message}")
                        continue
                time.sleep(config.get_delay_entre_requests())
        except KeyboardInterrupt:
            print("\nProceso interrumpido por el usuario. El progreso ha sido guardado.")



    def save_progress(self):
        """
        Guarda el progreso actual en el archivo JSON de salida de forma segura.
        """        
        try:
            with self.file_handler.abrir_escritura(self.output_file, permisos=0o600) as f:
                json.dump(self.processed_data, f, indent=2, ensure_ascii=False)
            print("Progreso guardado.")
        except ValueError as e:
            print(f"Error de seguridad al guardar progreso: {e}")
            raise



    def run(self):
        """
        Ejecuta el proceso completo de extracción de posts.
        """
        
        self.login()
        self.load_progress()
        self.load_profiles()
        self.process_profiles()
        print("\n--- ¡Procesamiento completado! ---")
        print(f"Todos los datos están en {self.output_file}")
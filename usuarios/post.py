# Este script inicia sesión en Bluesky, carga perfiles de un archivo JSON,
# obtiene los posts de cada usuario y guarda los resultados en otro archivo JSON.
# Esta diseñado para reanudar el proceso en caso de interrupciones o errores, para así evitar repetir trabajo ya realizado.

# La informacion que se guarda incluye:
# - cid, que es el Content Identifier del post. Este es un identificador único que apunta al contenido específico del post en la red de Bluesky.
# - uri, que es el identificador único del post en Bluesky. Se diferencia del cid en que el uri es una referencia más amigable y legible para los usuarios,
# mientras que el cid es más técnico y específico para la gestión del contenido en la red.
# - createdAt, la fecha y hora de creación del post.
# - text, que es el contenido textual del post.
# - replyCount, que es el número de respuestas que ha recibido el post.
# - repostCount, que es el número de veces que el post ha sido compartido por otros usuarios.
# - likeCount, que es el número de "me gusta" que ha recibido el post.
# - hasEmbed, que indica si el post contiene algún tipo de contenido incrustado, como imágenes, videos o enlaces.


import os
import time
import json
from gestor.conexion import ConexionBluesky

class BlueskyPostsFetcher:
    """
    Clase para extraer posts de usuarios de Bluesky.

    Esta clase se conecta a Bluesky, lee perfiles de usuarios desde un archivo JSON 
    (generado previamente con la clase datosUsuario), extrae sus posts y los guarda 
    en un archivo JSON de salida. Incluye capacidad de reanudación automática.   
    

    """
    
    
    def __init__(self, handle=None, app_password=None, input_file=None, output_file=None, posts_per_user_limit=25):
        self.handle = handle or os.environ.get('BSKY_HANDLE')
        self.app_password = app_password or os.environ.get('BSKY_APP_PASSWORD')
        self.conexion = ConexionBluesky(self.handle, self.app_password)
        # Guardar el input y output en la carpeta 'almacen'
        if input_file is None:
            input_file = os.path.join('almacen', 'profiles_to_scan.json')
        else:
            input_file = os.path.join('almacen', input_file) if not input_file.startswith('almacen'+os.sep) else input_file
        if output_file is None:
            output_file = os.path.join('almacen', 'posts_usuarios.json')
        else:
            output_file = os.path.join('almacen', output_file) if not output_file.startswith('almacen'+os.sep) else output_file
        # Crear la carpeta si no existe
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        self.input_file = input_file
        self.output_file = output_file
        self.posts_per_user_limit = posts_per_user_limit
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
        if os.path.exists(self.output_file):
            print(f"Cargando progreso existente desde {self.output_file}...")
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    self.processed_data = json.load(f)
                    self.processed_dids = set(self.processed_data.keys())
                    print(f"Progreso cargado. {len(self.processed_dids)} usuarios ya procesados.")
            except json.JSONDecodeError:
                print(f"Advertencia: {self.output_file} está corrupto. Empezando de cero.")
                self.processed_data = {}
                self.processed_dids = set()
        else:
            print("No se encontró archivo de progreso. Empezando de cero.")

    def load_profiles(self):
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.profiles_to_scan = json.load(f)
            print(f"Se cargarán {len(self.profiles_to_scan)} perfiles desde {self.input_file}.")
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: No se encontró el archivo {self.input_file}. Asegúrate de ejecutar 'fetch_profiles.py' primero.")

    def process_profiles(self):
        total_profiles = len(self.profiles_to_scan)
        try:
            for i, profile in enumerate(self.profiles_to_scan):
                did = profile.get('did')
                handle = profile.get('handle', 'N/A')
                print(f"\n--- Procesando {i+1}/{total_profiles}: {handle} ({did}) ---")
                if did in self.processed_dids:
                    print("Resultado ya existe. Omitiendo.")
                    continue
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
                    print(f"ERROR al procesar {handle}: {e}")
                    if "RateLimitExceeded" in str(e):
                        print("¡Límite de tasa alcanzado! Pausando 60 segundos...")
                        time.sleep(60)
                    else:
                        self.processed_data[did] = {"profile": profile, "posts": [], "error": str(e)}
                        self.save_progress()
                        time.sleep(1)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nProceso interrumpido por el usuario. El progreso ha sido guardado.")

    def save_progress(self):
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.processed_data, f, indent=2, ensure_ascii=False)
        print("Progreso guardado.")

    def run(self):
        self.login()
        self.load_progress()
        self.load_profiles()
        self.process_profiles()
        print("\n--- ¡Procesamiento completado! ---")
        print(f"Todos los datos están en {self.output_file}")
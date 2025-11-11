# Este script maneja la autenticación y la obtención de seguidores de una cuenta Bluesky. Los seguidores se guardan en un archivo JSON para su posterior procesamiento.
# Los seguidores se obtienen en páginas para manejar grandes cantidades de datos y evitar límites de la API. Con pausa entre solicitudes para respetar las políticas de la API.
# Los datos conseguidos son:
# 1. Datos de usuario:
# - DID, el cual es el identificador único de cada usuario en Bluesky
# - handle, que es el nombre de usuario público en Bluesky. El usuario puede cambiar su handle, pero el DID permanece constante.
# - display_name, que es el nombre que el usuario elige mostrar en su perfil. Este puede incluir caracteres especiales y emojis.
# - description, que es la biografía del usuario en su perfil.
# - avatar, que es la URL de la imagen de perfil del usuario.
# - pronouns, que son los pronombres que el usuario ha especificado en su perfil (si los ha proporcionado).
# - created_at, que es la fecha y hora en que se creó la cuenta del usuario en Bluesky.

# 2. Datos de actividad:
# - indexed_at, que es la fecha y hora en la que la red de Bluesky indexó por última vez el perfil del usuario.
# - labels, que son etiquetas asociadas al usuario, si vemos spam, impersonation, etc. significan que el usuario ha sido marcado por violar las reglas de la comunidad.
# - verification, que indica si el usuario ha sido verificado por Bluesky, lo que generalmente significa que es una figura pública o una cuenta oficial.
# - status, que indica el estado actual de la cuenta del usuario, como activo, suspendido, etc.

# 3. Datos de visor (Tu relación con el usuario):
# - blocked_by, false si no estás bloqueado por el usuario.
# - blocking, false si no has bloqueado al usuario.
# - following, si sigues al usuario.
# - followed_by, si el usuario te sigue a ti.
# - muted, si has silenciado al usuario.

# 4. Datos técnicos:
# - associated, que incluye información técnica sobre la cuenta del usuario, como si tiene una cuenta de invitado, si es una cuenta de servicio, etc.
# - py_type, que es un campo técnico utilizado internamente por la API de Bluesky.




import os
import time
import json
from gestor.conexion import ConexionBluesky

class datosUsuario:
    """
    Clase para manejar la autenticación y obtención de seguidores de una cuenta Bluesky.
    
    Attributes:
        handle (str): El identificador de la cuenta Bluesky.
        app_password (str): La contraseña de la aplicación para la cuenta Bluesky.
        client (Client): Instancia del cliente de la API de Bluesky.
        logged_in (bool): Estado de inicio de sesión.
        
    Methods:
        login(): Inicia sesión en la cuenta Bluesky.
        fetch_followers(target_account_handle, profile_limit=1000, page_limit=100, sleep_between_pages=2):
            Obtiene los seguidores de la cuenta objetivo.
        save_profiles(profiles, output_filename="profiles_to_scan.json"): Guarda los perfiles obtenidos en un archivo JSON.    
    """
    
    
    def __init__(self, handle=None, app_password=None):
        self.handle = handle or os.environ.get('BSKY_HANDLE')
        self.app_password = app_password or os.environ.get('BSKY_APP_PASSWORD')
        self.conexion = ConexionBluesky(self.handle, self.app_password)
        self.client = None

    def login(self):
        """
        Inicia sesión en la cuenta Bluesky usando ConexionBluesky.
        """
        self.client = self.conexion.get_client()



    def fetch_followers(self, target_account_handle, profile_limit=1000, page_limit=100, sleep_between_pages=2):
        """
        Obtiene los seguidores de la cuenta objetivo.
        Args:
            target_account_handle (str): El handle de la cuenta objetivo.
            profile_limit (int): Número máximo de perfiles a obtener.
            page_limit (int): Número de perfiles por página.
            sleep_between_pages (int): Segundos a esperar entre solicitudes de página.
        Returns:
            list: Lista de perfiles de seguidores obtenidos.
        Raises:
            RuntimeError: Si no se ha iniciado sesión antes de llamar a este método.
            """
        
        if not self.client:
            raise RuntimeError("Debes iniciar sesión antes de obtener seguidores.")
        
        all_profiles = []
        cursor = None
        print(f"\nEmpezando a obtener seguidores de {target_account_handle}...")
        
        try:
            while len(all_profiles) < profile_limit:
                print(f"Obteniendo página... (Total: {len(all_profiles)})")
                
                try:
                    response = self.client.get_followers(
                        actor=target_account_handle,
                        limit=page_limit,
                        cursor=cursor
                    )
                    if not response.followers:
                        print("No se encontraron más seguidores.")
                        break
                    
                    for profile in response.followers:
                        all_profiles.append(profile.model_dump(mode='json'))
                        if len(all_profiles) >= profile_limit:
                            break
                        
                    cursor = response.cursor
                    if not cursor:
                        print("Fin de la lista de seguidores.")
                        break
                    time.sleep(sleep_between_pages)
                    
                except Exception as e:
                    print(f"Error durante la solicitud a la API: {e}. Esperando 60s...")
                    time.sleep(60)
                    
        except KeyboardInterrupt:
            print("\nProceso interrumpido.")
        print(f"\nProceso finalizado. Total de perfiles obtenidos: {len(all_profiles)}")
        return all_profiles



    def save_profiles(self, profiles, output_filename="profiles_to_scan.json"):
        """
        Guarda los perfiles obtenidos en un archivo JSON.
        Args:
            profiles (list): Lista de perfiles a guardar.
            output_filename (str): Nombre del archivo de salida.
        """
        
        if not profiles:
            print("No hay perfiles para guardar.")
            return
        
        print(f"Guardando {len(profiles)} perfiles en {output_filename}...")
        
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(profiles, f, indent=4, ensure_ascii=False)
            print(f"¡Datos guardados! Ahora puedes ejecutar 'fetch_posts.py'.")
            
        except Exception as e:
            print(f"Error al guardar el archivo JSON: {e}")
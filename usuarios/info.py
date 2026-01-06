import os
import sys
import time
import json
from pathlib import Path

# Agregar ruta del proyecto para imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gestor.conexion import ConexionBluesky
from seguridad.secure_file_handler import SecureFileHandler

class datosUsuario:
    """
    Clase para manejar la autenticación y obtención de seguidores de una cuenta Bluesky.
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
        Obtiene los seguidores. CORREGIDO: No espera 60s si el usuario no existe.
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
                    mensaje_error = str(e)
                    
                    # --- CAMBIO IMPORTANTE: DETECCIÓN DE ERRORES ---
                    
                    # Caso 1: El usuario no existe o está mal escrito
                    if "Actor not found" in mensaje_error or "Profile not found" in mensaje_error:
                        print(f"   [X] ERROR FATAL: La cuenta '{target_account_handle}' no existe. Saltando inmediatamente.")
                        break # Rompe el bucle y deja de intentar con este usuario
                    
                    # Caso 2: Límite de velocidad de la API (Aquí sí esperamos)
                    elif "RateLimit" in mensaje_error or "429" in mensaje_error:
                        print(f"   [!] Límite de API alcanzado. Esperando 60s...")
                        time.sleep(60)
                        
                    # Caso 3: Cualquier otro error desconocido
                    else:
                        print(f"   [!] Error desconocido: {e}. Saltando para evitar bucles infinitos.")
                        break
                    
        except KeyboardInterrupt:
            print("\nProceso interrumpido.")
            
        print(f"Proceso finalizado para {target_account_handle}. Total obtenidos: {len(all_profiles)}")
        return all_profiles

    def save_profiles(self, profiles, output_filename="profiles_to_scan.json"):
        """
        Guarda los perfiles obtenidos en un archivo JSON de forma segura.
        """
        if not profiles:
            print("No hay perfiles nuevos para guardar de esta ejecución.")
            return
        
        try:
            # Determinar directorio base seguro
            project_root = Path(__file__).parent.parent
            almacen_dir = project_root / 'almacen'
            
            # Crear handler seguro
            handler = SecureFileHandler(almacen_dir)
            
            # Leer perfiles existentes si el archivo existe
            existing_profiles = []
            if handler.existe(output_filename):
                try:
                    with handler.abrir_lectura(output_filename) as f:
                        existing_profiles = json.load(f)
                except Exception as e:
                    print(f"Advertencia: No se pudieron cargar perfiles existentes: {e}")
            
            # Evitar duplicados por DID
            existing_dids = {p.get('did') for p in existing_profiles if 'did' in p}
            new_profiles = [p for p in profiles if p.get('did') not in existing_dids]
            
            if not new_profiles:
                print("Todos los perfiles descargados ya existían en la base de datos.")
                return

            all_profiles = existing_profiles + new_profiles
            print(f"Guardando {len(new_profiles)} perfiles nuevos (total acumulado: {len(all_profiles)}) en {output_filename}...")
            
            # Guardar con permisos restrictivos (solo propietario puede leer/escribir)
            with handler.abrir_escritura(output_filename, permisos=0o600) as f:
                json.dump(all_profiles, f, indent=4, ensure_ascii=False)
            print(f"¡Datos guardados correctamente!")
            
        except ValueError as e:
            print(f"Error de seguridad: {e}")
            raise
        except Exception as e:
            print(f"Error al guardar el archivo JSON: {e}")
            raise
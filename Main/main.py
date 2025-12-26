import sys
import os
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from usuarios.info import datosUsuario
from usuarios.post import BlueskyPostsFetcher
from configuracion.load_config import config

class MainApp:
    """
    Clase principal con semillas 100% VERIFICADAS y SEGURAS (Medios e Instituciones).
    Evita errores de 'Actor not found' usando cuentas que no desaparecen.
    """

    def __init__(self, bsky_handle=None, bsky_app_password=None, output_filename=None):
        self.bsky_handle = bsky_handle
        self.bsky_app_password = bsky_app_password
        
        # --- CONFIGURACIÓN DESDE YAML ---
        self.usuarios_por_semilla = config.get_usuarios_por_semilla()
        self.pool_size = config.get_pool_size()

        # 3. Las Semillas (CUENTAS DE ALTA ESTABILIDAD)
        # He quitado cuentas personales dudosas y puesto grandes medios/instituciones
        self.semillas = {
            "tecnologia": [
                "verge.bsky.social",     # The Verge
                "wired.com",             # Wired
                "mkbhd.bsky.social"      # MKBHD (Muy estable)
            ],
            "politica_y_noticias": [
                "aoc.bsky.social",       # AOC (Muy activa y verificada)
                "nytimes.com",           # The New York Times (No va a desaparecer)
                "npr.org",               # NPR (Radio pública EEUU)
                "washingtonpost.com"     # Washington Post
            ],
            "entretenimiento": [
                "jamesgunn.bsky.social", # James Gunn
                "stephenking.bsky.social" # Stephen King
            ],
            "ciencia": [
                "astrokatie.bsky.social",    # Katie Mack (Astrofísica muy popular y activa)
                "ericholthaus.bsky.social"   # Eric Holthaus (Meteorólogo y experto en clima)
            ],
             "deportes": [
                "jeffpassan.bsky.social", # Jeff Passan (Periodista deportivo)
                "rosenthal.bsky.social", # Ken Rosenthal (Periodista deportivo)
                "theathletic.com"        # The Athletic
            ]
        }
        # ---------------------------------------------------------

        if output_filename is None:
            # Usar ruta desde configuración
            output_filename = config.get_ruta_profiles()
        else:
            directorio = config.get('rutas', 'directorio_almacen')
            output_filename = os.path.join(directorio, output_filename) if not output_filename.startswith(directorio+os.sep) else output_filename

        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        self.output_filename = output_filename
        self.fetcher = datosUsuario(self.bsky_handle, self.bsky_app_password)

    def run(self):
        try:
            self.fetcher.login()
            
            lista_maestra_usuarios = [] 
            total_semillas = sum(len(v) for v in self.semillas.values())
            contador_semillas = 0

            print(f"--- INICIANDO EXTRACCIÓN ESTABLE ---")
            print(f"Guardando en: {self.output_filename}")

            for categoria, cuentas_famosas in self.semillas.items():
                print(f"\n>>> CATEGORÍA: {categoria.upper()}")
                
                for famoso in cuentas_famosas:
                    contador_semillas += 1
                    print(f"   [{contador_semillas}/{total_semillas}] Extrayendo de: {famoso}...")
                    
                    try:
                        seguidores_crudos = self.fetcher.fetch_followers(
                            target_account_handle=famoso,
                            profile_limit=self.pool_size,
                            page_limit=config.get_page_limit()
                        )
                        
                        if seguidores_crudos:
                            cantidad_a_elegir = min(len(seguidores_crudos), self.usuarios_por_semilla)
                            elegidos = random.sample(seguidores_crudos, cantidad_a_elegir)
                            
                            for u in elegidos:
                                u['origen_categoria'] = categoria
                                u['origen_semilla'] = famoso
                                
                            lista_maestra_usuarios.extend(elegidos)
                            print(f"      [OK] Seleccionados {len(elegidos)} usuarios de {famoso}.")
                        else:
                            # Si llega aquí es que la cuenta existe pero no dio datos
                            print(f"      [!] Aviso: {famoso} no devolvió seguidores.")
                            
                    except Exception as e:
                        # Si falla, imprimimos y SALTAMOS al siguiente (continue)
                        # Esto evita que el programa principal se detenga
                        print(f"      [X] FALLO en {famoso}. Saltando a la siguiente cuenta. Error: {e}")
                        continue 

            print(f"\n--- GUARDANDO DATOS ---")
            self.fetcher.save_profiles(lista_maestra_usuarios, output_filename=self.output_filename)

            print("\n--- EXTRACCIÓN DE POSTS ---")
            posts_fetcher = BlueskyPostsFetcher(
                handle=self.bsky_handle,
                app_password=self.bsky_app_password,
                input_file=os.path.basename(self.output_filename),
                output_file=None,
                posts_per_user_limit=config.get_posts_por_usuario_limite()
            )
            posts_fetcher.run()

        except Exception as e:
            print(f"Error crítico en el loop principal: {e}")

if __name__ == "__main__":
    app = MainApp()
    app.run()
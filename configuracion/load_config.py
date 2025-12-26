"""
Módulo para cargar la configuración centralizada del proyecto desde config.yaml
"""
import os
import yaml
from pathlib import Path

class Config:
    """Clase para gestionar la configuración del proyecto"""
    
    _instance = None
    _config_data = None
    
    def __new__(cls):
        """Singleton pattern - solo una instancia de Config"""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa y carga la configuración si no está cargada"""
        if self._config_data is None:
            self._load_config()
    
    def _load_config(self):
        """Carga el archivo config.yaml"""
        # Obtener la ruta del directorio del proyecto
        project_root = Path(__file__).parent.parent
        config_path = project_root / 'configuracion' / 'config.yaml'
        
        if not config_path.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo de configuración: {config_path}\n"
                "Asegúrate de que existe configuracion/config.yaml"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config_data = yaml.safe_load(f)
    
    def get(self, *keys, default=None):
        """
        Obtiene un valor de la configuración usando notación de puntos.
        
        Ejemplos:
            config.get('spark', 'driver_memory')  -> "8g"
            config.get('scraping', 'usuarios_por_semilla')  -> 10
            config.get('rutas', 'archivo_posts_json')  -> "posts_usuarios.json"
        
        Args:
            *keys: Claves para navegar en la estructura del YAML
            default: Valor por defecto si no se encuentra la clave
            
        Returns:
            El valor encontrado o el default
        """
        data = self._config_data
        
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return default
        
        return data
    
    def get_ruta_completa(self, *keys):
        """
        Obtiene una ruta completa combinando el directorio almacen con el archivo.
        
        Ejemplo:
            config.get_ruta_completa('rutas', 'archivo_posts_json')
            -> "almacen/posts_usuarios.json"
        """
        directorio = self.get('rutas', 'directorio_almacen')
        archivo = self.get(*keys)
        
        if archivo and directorio:
            return os.path.join(directorio, archivo)
        
        return archivo
    
    # ── Métodos de acceso rápido ──
    
    # Rutas
    def get_ruta_profiles(self):
        """Retorna la ruta completa a profiles_to_scan.json"""
        return self.get_ruta_completa('rutas', 'archivo_profiles')
    
    def get_ruta_posts_json(self):
        """Retorna la ruta completa a posts_usuarios.json"""
        return self.get_ruta_completa('rutas', 'archivo_posts_json')
    
    def get_ruta_posts_jsonl(self):
        """Retorna la ruta completa a posts_usuarios.jsonl"""
        return self.get_ruta_completa('rutas', 'archivo_posts_jsonl')
    
    # Scraping
    def get_usuarios_por_semilla(self):
        """Retorna el número de usuarios por semilla"""
        return self.get('scraping', 'usuarios_por_semilla', default=10)
    
    def get_pool_size(self):
        """Retorna el tamaño del pool de usuarios"""
        return self.get('scraping', 'pool_size', default=12)
    
    def get_page_limit(self):
        """Retorna el límite de páginas"""
        return self.get('scraping', 'page_limit', default=100)
    
    # Posts
    def get_posts_por_usuario_limite(self):
        """Retorna el límite de posts por usuario"""
        return self.get('posts', 'posts_por_usuario_limite', default=25)
    
    def get_delay_entre_requests(self):
        """Retorna el delay entre requests"""
        return self.get('posts', 'delay_entre_requests', default=1)
    
    def get_delay_rate_limit(self):
        """Retorna el delay cuando hay rate limit"""
        return self.get('posts', 'delay_rate_limit', default=60)
    
    # Spark
    def get_spark_config(self):
        """Retorna toda la configuración de Spark como diccionario"""
        return self.get('spark', default={})
    
    def get_java_home(self):
        """Retorna la ruta de JAVA_HOME"""
        return self.get('spark', 'java_home')
    
    # Análisis
    def get_top_n_resultados(self):
        """Retorna el número de resultados para Top N"""
        return self.get('analisis', 'top_n_resultados', default=10)
    
    def get_filas_mostrar(self):
        """Retorna el número de filas a mostrar"""
        return self.get('analisis', 'filas_mostrar', default=15)
    
    def get_truncar_tablas(self):
        """Retorna el valor de truncado para tablas"""
        return self.get('analisis', 'truncar_tablas', default=50)

# Instancia global de configuración
config = Config()

# Ejemplo de uso en otros módulos:
# from configuracion.load_config import config
# driver_memory = config.get('spark', 'driver_memory')
# usuarios_por_semilla = config.get_usuarios_por_semilla()

"""
Módulo para manejo seguro de archivos con validación de rutas.
Previene ataques de path traversal, symlink attacks y acceso no autorizado.
"""
import os
from pathlib import Path


class SecureFileHandler:
    """Manejo seguro de archivos con validación de rutas"""
    
    def __init__(self, base_dir):
        """
        Inicializa el handler con un directorio base permitido.
        
        Args:
            base_dir: Directorio base permitido (se convertirá a absoluto)
        
        Raises:
            ValueError: Si el directorio base no existe o no es válido
        """
        self.base_dir = Path(base_dir).resolve()
        
        if not self.base_dir.exists():
            raise ValueError(f"El directorio base no existe: {self.base_dir}")
        
        if not self.base_dir.is_dir():
            raise ValueError(f"La ruta base no es un directorio: {self.base_dir}")
    
    def validar_ruta(self, ruta):
        """
        Valida que la ruta esté dentro del directorio permitido.
        
        Previene:
        - Path traversal (../)
        - Symlink attacks
        - Acceso a archivos fuera del directorio base
        
        Args:
            ruta: Ruta del archivo a validar (relativa o absoluta)
        
        Returns:
            Path: Ruta absoluta validada y segura
        
        Raises:
            ValueError: Si la ruta intenta salir del directorio permitido
        """
        try:
            # Convertir a Path y obtener ruta absoluta
            if isinstance(ruta, str):
                ruta = Path(ruta)
            
            # Si es relativa, combinar con base_dir
            if not ruta.is_absolute():
                ruta_absoluta = (self.base_dir / ruta).resolve()
            else:
                ruta_absoluta = ruta.resolve()
            
            # Verificar que está dentro del directorio permitido
            # relative_to lanzará ValueError si no está dentro
            ruta_absoluta.relative_to(self.base_dir)
            
            return ruta_absoluta
            
        except (ValueError, OSError) as e:
            raise ValueError(
                f"Acceso denegado: la ruta '{ruta}' está fuera del directorio permitido '{self.base_dir}'. "
                f"Error: {e}"
            )
    
    def abrir_lectura(self, ruta, modo='r', encoding='utf-8'):
        """
        Abre un archivo de forma segura para lectura.
        
        Args:
            ruta: Ruta del archivo (relativa al base_dir o absoluta dentro de base_dir)
            modo: Modo de apertura ('r' o 'rb')
            encoding: Codificación del archivo (solo para modo texto)
        
        Returns:
            File object
        
        Raises:
            ValueError: Si la ruta no es segura
            FileNotFoundError: Si el archivo no existe
        """
        ruta_segura = self.validar_ruta(ruta)
        
        # Verificar que el archivo existe
        if not ruta_segura.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {ruta_segura}")
        
        # Verificar que es un archivo regular (no un directorio o dispositivo)
        if not ruta_segura.is_file():
            raise ValueError(f"No es un archivo regular: {ruta_segura}")
        
        # Abrir el archivo
        if 'b' in modo:
            return open(ruta_segura, modo)
        else:
            return open(ruta_segura, modo, encoding=encoding)
    
    def abrir_escritura(self, ruta, modo='w', encoding='utf-8', permisos=0o600):
        """
        Abre un archivo de forma segura para escritura con permisos restrictivos.
        
        Args:
            ruta: Ruta del archivo (relativa al base_dir o absoluta dentro de base_dir)
            modo: Modo de apertura ('w', 'wb', 'a', 'ab')
            encoding: Codificación del archivo (solo para modo texto)
            permisos: Permisos del archivo (por defecto 0o600 = solo propietario)
        
        Returns:
            File object
        
        Raises:
            ValueError: Si la ruta no es segura
        """
        ruta_segura = self.validar_ruta(ruta)
        
        # Crear directorio padre si no existe (de forma segura)
        ruta_segura.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        # Determinar flags según el modo
        flags = os.O_WRONLY | os.O_CREAT
        
        if 'a' in modo:
            flags |= os.O_APPEND
        else:
            flags |= os.O_TRUNC
        
        # Abrir con permisos restrictivos usando os.open
        # Esto previene race conditions (TOCTOU)
        fd = os.open(ruta_segura, flags, permisos)
        
        # Convertir el file descriptor a un objeto file
        if 'b' in modo:
            return open(fd, modo)
        else:
            return open(fd, modo, encoding=encoding)
    
    def existe(self, ruta):
        """
        Verifica si un archivo existe de forma segura.
        
        Args:
            ruta: Ruta del archivo
        
        Returns:
            bool: True si existe, False si no
        
        Raises:
            ValueError: Si la ruta no es segura
        """
        try:
            ruta_segura = self.validar_ruta(ruta)
            return ruta_segura.exists()
        except ValueError:
            return False
    
    def es_archivo(self, ruta):
        """
        Verifica si una ruta es un archivo regular de forma segura.
        
        Args:
            ruta: Ruta a verificar
        
        Returns:
            bool: True si es un archivo, False si no
        
        Raises:
            ValueError: Si la ruta no es segura
        """
        try:
            ruta_segura = self.validar_ruta(ruta)
            return ruta_segura.is_file()
        except ValueError:
            return False

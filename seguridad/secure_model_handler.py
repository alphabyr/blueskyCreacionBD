"""
Módulo para carga/guardado seguro de modelos ML con validación de integridad.
Previene ataques de deserialización insegura con pickle.
"""
import pickle
import hashlib
import json
from pathlib import Path


class SecureModelHandler:
    """Manejo seguro de modelos ML con verificación de integridad"""
    
    def __init__(self, modelos_dir):
        """
        Args:
            modelos_dir: Directorio donde se almacenan los modelos
        """
        self.modelos_dir = Path(modelos_dir)
        self.checksums_file = self.modelos_dir / 'checksums.json'
    
    def calcular_checksum(self, archivo):
        """Calcula el hash SHA-256 de un archivo"""
        sha256 = hashlib.sha256()
        with open(archivo, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def guardar_modelo(self, modelo, nombre_archivo, permisos=0o600):
        """
        Guarda un modelo y registra su checksum.
        
        Args:
            modelo: Objeto a serializar
            nombre_archivo: Nombre del archivo (ej: 'bot_detector.pkl')
            permisos: Permisos del archivo (por defecto solo propietario)
        
        Returns:
            Path: Ruta donde se guardó el modelo
        """
        ruta = self.modelos_dir / nombre_archivo
        
        # Crear directorio si no existe
        self.modelos_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar modelo con permisos restrictivos
        import os
        fd = os.open(ruta, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, permisos)
        with open(fd, 'wb') as f:
            pickle.dump(modelo, f)
        
        # Calcular y guardar checksum
        checksum = self.calcular_checksum(ruta)
        self._guardar_checksum(nombre_archivo, checksum)
        
        return ruta
    
    def cargar_modelo(self, nombre_archivo, verificar_integridad=True):
        """
        Carga un modelo verificando su integridad.
        
        Args:
            nombre_archivo: Nombre del archivo a cargar
            verificar_integridad: Si True, verifica el checksum antes de cargar
        
        Returns:
            Objeto deserializado
        
        Raises:
            ValueError: Si el archivo ha sido modificado
            FileNotFoundError: Si el archivo no existe
        """
        ruta = self.modelos_dir / nombre_archivo
        
        if not ruta.exists():
            raise FileNotFoundError(f"Modelo no encontrado: {ruta}")
        
        # Verificar integridad si está habilitado
        if verificar_integridad:
            checksum_esperado = self._obtener_checksum(nombre_archivo)
            if checksum_esperado:
                checksum_actual = self.calcular_checksum(ruta)
                if checksum_actual != checksum_esperado:
                    raise ValueError(
                        f"⚠️ ALERTA DE SEGURIDAD: El archivo '{nombre_archivo}' ha sido modificado. "
                        f"Checksum esperado: {checksum_esperado[:16]}..., "
                        f"Checksum actual: {checksum_actual[:16]}... "
                        f"No se cargará el modelo por seguridad."
                    )
            else:
                print(f"⚠️ Advertencia: No hay checksum registrado para {nombre_archivo}. "
                      f"Cargando sin verificación de integridad.")
        
        # Cargar el modelo
        with open(ruta, 'rb') as f:
            return pickle.load(f)
    
    def _guardar_checksum(self, nombre_archivo, checksum):
        """Guarda el checksum de un archivo"""
        checksums = self._cargar_checksums()
        checksums[nombre_archivo] = checksum
        
        with open(self.checksums_file, 'w') as f:
            json.dump(checksums, f, indent=2)
    
    def _obtener_checksum(self, nombre_archivo):
        """Obtiene el checksum guardado de un archivo"""
        checksums = self._cargar_checksums()
        return checksums.get(nombre_archivo)
    
    def _cargar_checksums(self):
        """Carga el registro de checksums"""
        if self.checksums_file.exists():
            try:
                with open(self.checksums_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def listar_modelos(self):
        """Lista todos los modelos con sus checksums"""
        checksums = self._cargar_checksums()
        modelos = []
        
        for archivo in self.modelos_dir.glob('*.pkl'):
            nombre = archivo.name
            checksum = checksums.get(nombre, 'No registrado')
            tamanio = archivo.stat().st_size
            modelos.append({
                'nombre': nombre,
                'checksum': checksum[:16] + '...' if checksum != 'No registrado' else checksum,
                'tamanio_bytes': tamanio
            })
        
        return modelos
    
    def verificar_todos(self):
        """Verifica la integridad de todos los modelos guardados"""
        checksums = self._cargar_checksums()
        resultados = []
        
        for nombre_archivo, checksum_esperado in checksums.items():
            ruta = self.modelos_dir / nombre_archivo
            
            if not ruta.exists():
                resultados.append({
                    'archivo': nombre_archivo,
                    'estado': '❌ FALTA',
                    'mensaje': 'Archivo no encontrado'
                })
                continue
            
            checksum_actual = self.calcular_checksum(ruta)
            
            if checksum_actual == checksum_esperado:
                resultados.append({
                    'archivo': nombre_archivo,
                    'estado': '✓ OK',
                    'mensaje': 'Integridad verificada'
                })
            else:
                resultados.append({
                    'archivo': nombre_archivo,
                    'estado': '⚠️ MODIFICADO',
                    'mensaje': 'El archivo ha sido alterado'
                })
        
        return resultados

from pyspark.sql import SparkSession

class CargaDatos:
    def __init__(self, spark):
        # Recibe una SparkSession existente
        self.spark = spark

    def cargar_posts_usuarios(self, ruta):
        """
        Carga los datos del archivo posts_usuarios.jsonl en un DataFrame de Spark.
        El archivo debe estar en formato JSONL (JSON Lines) con un post por línea.
        
        Cada línea contiene: usuario_did, usuario_handle, cid, uri, createdAt, text, etc.

        :param ruta: Ruta al archivo posts_usuarios.jsonl
        :return: DataFrame con un post por fila
        """
        import os
        
        if not os.path.exists(ruta):
            print(f"Error: No se encontró el archivo {ruta}")
            return None
        
        try:
            print(f"Cargando {ruta}...")
            
            # Leer archivo JSONL directamente
            # Cada línea es un post individual
            df = self.spark.read.json(ruta)
            
            count = df.count()
            print(f"✓ Datos cargados: {count} posts")
            return df
            
        except Exception as e:
            print(f"Error al cargar posts_usuarios: {e}")
            import traceback
            traceback.print_exc()
            return None

    def cargar_profiles_to_scan(self, ruta):
        """
        Carga los datos del archivo profiles_to_scan.json en un DataFrame de Spark.
        Se utiliza la opción multiline=true para archivos JSON donde los objetos
        ocupan varias líneas o están en un array JSON grande.

        :param ruta: Ruta al archivo profiles_to_scan.json
        :return: DataFrame con los datos cargados
        """
        try:
            # CORRECCIÓN: Usar .option("multiline", "true") para archivos JSON grandes/arrays
            df_profiles_to_scan = self.spark.read.option("multiline", "true").json(ruta)
            print("Datos de profiles_to_scan cargados correctamente (multilínea).")
            return df_profiles_to_scan
        except Exception as e:
            print(f"Error al cargar profiles_to_scan: {e}")
            return None # Devolver None en caso de error para evitar fallos posteriores
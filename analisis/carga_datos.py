from pyspark.sql import SparkSession

class CargaDatos:
    def __init__(self, spark):
        # Recibe una SparkSession existente
        self.spark = spark

    def cargar_posts_usuarios(self, ruta):
        """
        Carga los datos del archivo posts_usuarios.json en un DataFrame de Spark.
        Se utiliza la opción multiline=true para archivos JSON donde los objetos
        ocupan varias líneas o están en un array JSON grande.

        :param ruta: Ruta al archivo posts_usuarios.json
        :return: DataFrame con los datos cargados
        """
        try:
            # CORRECCIÓN: Usar .option("multiline", "true") para archivos JSON grandes/arrays
            df_posts_usuarios = self.spark.read.option("multiline", "true").json(ruta)
            print("Datos de posts_usuarios cargados correctamente (multilínea).")
            return df_posts_usuarios
        except Exception as e:
            print(f"Error al cargar posts_usuarios: {e}")
            return None # Devolver None en caso de error para evitar fallos posteriores

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
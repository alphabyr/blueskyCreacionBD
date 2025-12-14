from pyspark.sql.functions import col, count, expr, to_date, min, max, avg

class AnalizarProfiles:
    def __init__(self, spark):
        # Recibe una SparkSession existente
        self.spark = spark

    def cargar_datos(self, ruta):
        """
        Carga los datos de un archivo JSON en un DataFrame de Spark.

        :param ruta: Ruta al archivo JSON
        :return: DataFrame con los datos cargados
        """
        try:
            df = self.spark.read.json(ruta)
            print(f"Datos cargados correctamente desde {ruta}.")
            return df
        except Exception as e:
            print(f"Error al cargar datos desde {ruta}: {e}")

    def contar_perfiles(self, df):
        """
        Cuenta el número total de perfiles en el DataFrame.

        :param df: DataFrame de Spark
        :return: Número total de perfiles
        """
        total = df.count()
        print(f"Número total de perfiles: {total}")
        return total

    def analizar_origenes(self, df):
        """
        Analiza la distribución de perfiles por categoría y semilla de origen.

        :param df: DataFrame de Spark
        """
        try:
            print("Distribución por categoría de origen:")
            df.groupBy("origen_categoria").count().orderBy(col("count").desc()).show()

            print("Distribución por semilla de origen:")
            df.groupBy("origen_semilla").count().orderBy(col("count").desc()).show()
        except Exception as e:
            print(f"Error al analizar los orígenes: {e}")

    def analizar_fechas_creacion(self, df):
        """
        Analiza las fechas de creación de los perfiles, mostrando el rango y la distribución por año y mes.

        :param df: DataFrame de Spark
        """
        try:
            df = df.withColumn("fecha_creacion", to_date(col("created_at")))
            rango_fechas = df.select(min("fecha_creacion").alias("Fecha mínima"), max("fecha_creacion").alias("Fecha máxima")).collect()[0]
            print(f"Rango de fechas de creación: {rango_fechas['Fecha mínima']} a {rango_fechas['Fecha máxima']}")

            print("Distribución por año de creación:")
            df.groupBy(expr("year(fecha_creacion)").alias("Anio")).count().orderBy("Anio").show()

            print("Distribución por mes de creación:")
            df.groupBy(expr("year(fecha_creacion) as Anio"), expr("month(fecha_creacion) as Mes")).count().orderBy("Anio", "Mes").show()
        except Exception as e:
            print(f"Error al analizar las fechas de creación: {e}")

    def analizar_descripciones(self, df):
        """
        Analiza las descripciones de los perfiles, mostrando estadísticas sobre su longitud.

        :param df: DataFrame de Spark
        """
        try:
            df = df.withColumn("longitud_descripcion", expr("length(description)"))
            stats = df.select(
                min("longitud_descripcion").alias("Longitud mínima"),
                max("longitud_descripcion").alias("Longitud máxima"),
                avg("longitud_descripcion").alias("Longitud promedio")
            ).collect()[0]

            print("Análisis de las descripciones de los perfiles:")
            print(f"Longitud mínima: {stats['Longitud mínima']}")
            print(f"Longitud máxima: {stats['Longitud máxima']}")
            print(f"Longitud promedio: {stats['Longitud promedio']}")
        except Exception as e:
            print(f"Error al analizar las descripciones: {e}")

    def analizar_verificaciones(self, df):
        """
        Analiza el estado de verificación de los perfiles.

        :param df: DataFrame de Spark
        """
        try:
            print("Distribución de perfiles verificados y no verificados:")
            df.groupBy("verification").count().orderBy(col("count").desc()).show()
        except Exception as e:
            print(f"Error al analizar el estado de verificación: {e}")
# pyspark_test.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, max, min, stddev, expr, to_date

class AnalizarPost:
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

    def contar_registros(self, df):
        """
        Cuenta el número total de registros en el DataFrame.

        :param df: DataFrame de Spark
        :return: Número total de registros
        """
        total = df.count()
        print(f"Número total de registros: {total}")
        return total

    def estadisticas_basicas(self, df, columna):
        """
        Calcula estadísticas básicas (mínimo, máximo, promedio, desviación estándar) para una columna numérica.

        :param df: DataFrame de Spark
        :param columna: Nombre de la columna para calcular estadísticas
        """
        try:
            stats = df.select(
                min(col(columna)).alias("Mínimo"),
                max(col(columna)).alias("Máximo"),
                avg(col(columna)).alias("Promedio"),
                stddev(col(columna)).alias("Desviación Estándar")
            ).collect()[0]

            print(f"Estadísticas básicas para la columna '{columna}':")
            print(f"Mínimo: {stats['Mínimo']}")
            print(f"Máximo: {stats['Máximo']}")
            print(f"Promedio: {stats['Promedio']}")
            print(f"Desviación Estándar: {stats['Desviación Estándar']}")
        except Exception as e:
            print(f"Error al calcular estadísticas para la columna '{columna}': {e}")

    def contar_valores_unicos(self, df, columna):
        """
        Cuenta el número de valores únicos en una columna específica.

        :param df: DataFrame de Spark
        :param columna: Nombre de la columna
        :return: Número de valores únicos
        """
        try:
            total_unicos = df.select(columna).distinct().count()
            print(f"Número de valores únicos en la columna '{columna}': {total_unicos}")
            return total_unicos
        except Exception as e:
            print(f"Error al contar valores únicos en la columna '{columna}': {e}")

    def mostrar_frecuencias(self, df, columna, limite=10):
        """
        Muestra las frecuencias de los valores más comunes en una columna.

        :param df: DataFrame de Spark
        :param columna: Nombre de la columna
        :param limite: Número de valores más comunes a mostrar
        """
        try:
            print(f"Frecuencias de los valores más comunes en la columna '{columna}':")
            df.groupBy(columna).count().orderBy(col("count").desc()).show(limite)
        except Exception as e:
            print(f"Error al mostrar frecuencias para la columna '{columna}': {e}")

    def analizar_fechas(self, df, columna_fecha):
        """
        Analiza las fechas en una columna, mostrando el rango de fechas y la distribución por año y mes.

        :param df: DataFrame de Spark
        :param columna_fecha: Nombre de la columna de fechas
        """
        try:
            df = df.withColumn("fecha", to_date(col(columna_fecha)))
            rango_fechas = df.select(min("fecha").alias("Fecha mínima"), max("fecha").alias("Fecha máxima")).collect()[0]
            print(f"Rango de fechas: {rango_fechas['Fecha mínima']} a {rango_fechas['Fecha máxima']}")

            print("Distribución por año:")
            df.groupBy(expr("year(fecha)").alias("Año")).count().orderBy("Año").show()

            print("Distribución por mes:")
            df.groupBy(expr("year(fecha) as Año"), expr("month(fecha) as Mes")).count().orderBy("Año", "Mes").show()
        except Exception as e:
            print(f"Error al analizar fechas en la columna '{columna_fecha}': {e}")

    def analizar_texto(self, df, columna_texto):
        """
        Analiza una columna de texto, mostrando la longitud promedio, mínima y máxima de los textos.

        :param df: DataFrame de Spark
        :param columna_texto: Nombre de la columna de texto
        """
        try:
            df = df.withColumn("longitud", expr(f"length({columna_texto})"))
            stats = df.select(
                min("longitud").alias("Longitud mínima"),
                max("longitud").alias("Longitud máxima"),
                avg("longitud").alias("Longitud promedio")
            ).collect()[0]

            print(f"Análisis de la columna de texto '{columna_texto}':")
            print(f"Longitud mínima: {stats['Longitud mínima']}")
            print(f"Longitud máxima: {stats['Longitud máxima']}")
            print(f"Longitud promedio: {stats['Longitud promedio']}")
        except Exception as e:
            print(f"Error al analizar la columna de texto '{columna_texto}': {e}")
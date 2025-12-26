import os
import sys

# Configurar Python para PySpark en Windows
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
os.environ['PYSPARK_PYTHON'] = sys.executable

# Configurar Java 17 para PySpark (en lugar de Java 8)
os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-17'

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode
from carga_datos import CargaDatos
from analizar_post import AnalizarPost
from analizar_profiles import AnalizarProfiles

def main():
    # Crear la SparkSession con configuración de memoria
    spark = SparkSession.builder \
        .appName("Bluesky Data Analysis") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.sql.debug.maxToStringFields", "1000") \
        .getOrCreate()

    # Instanciar las clases
    carga_datos = CargaDatos(spark)
    analizar_post = AnalizarPost(spark)
    analizar_profiles = AnalizarProfiles(spark)

    # Rutas de los archivos JSON (relativas al script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)  # Directorio bluesky2
    ruta_posts = os.path.join(base_dir, "almacen", "posts_usuarios.json")
    ruta_profiles = os.path.join(base_dir, "almacen", "profiles_to_scan.json")

    # Cargar datos
    print("Cargando datos de posts...")
    df_posts = carga_datos.cargar_posts_usuarios(ruta_posts)

    print("Cargando datos de perfiles...")
    df_profiles = carga_datos.cargar_profiles_to_scan(ruta_profiles)

    # Manejar registros corruptos
    if df_posts:
        if "_corrupt_record" in df_posts.columns:
            df_posts = df_posts.filter(col("_corrupt_record").isNull())
            print("Registros corruptos eliminados de posts.")
        df_posts = df_posts.cache()
        print("DataFrame de posts almacenado en caché.")


    if df_profiles:
        if "_corrupt_record" in df_profiles.columns:
            df_profiles = df_profiles.filter(col("_corrupt_record").isNull())
            print("Registros corruptos eliminados de perfiles.")
        df_profiles = df_profiles.cache()
        print("DataFrame de perfiles almacenado en caché.")

    # --- PASOS DE DIAGNÓSTICO ---
    if df_profiles:
        print("\n--- DIAGNÓSTICO DE df_profiles ---")
        df_profiles.printSchema()  # Muestra el esquema y las columnas
        print(f"Total de registros válidos después del filtro y cache: {df_profiles.count()}")
        df_profiles.limit(5).show(truncate=False)  # Muestra las primeras 5 filas (si existen)
        # --- FIN DIAGNÓSTICO ---

    # Análisis de posts_usuarios.json
    print("\n--- Análisis de Posts ---")
    if df_posts and "profile" in df_posts.columns:
        # Extraer la sección de perfiles
        try:
            df_profiles_from_posts = df_posts.selectExpr("profile.*")
            print("Análisis de perfiles extraídos de posts_usuarios.json:")
            analizar_profiles.contar_perfiles(df_profiles_from_posts)

            # Extraer y analizar publicaciones
            if "posts" in df_posts.columns:
                df_posts_exploded = df_posts.selectExpr("profile.did as user_did", "explode(posts) as post")
                if df_posts_exploded.count() > 0:
                    print("Análisis de publicaciones extraídas de posts_usuarios.json:")
                    analizar_post.contar_registros(df_posts_exploded)
                else:
                    print("No se encontraron publicaciones en posts_usuarios.json.")
            else:
                print("La columna 'posts' no está disponible en los datos de posts.")
        except Exception as e:
            print(f"Error al analizar los datos de posts_usuarios.json: {e}")
    else:
        print("La columna 'profile' no está disponible en los datos de posts o no hay datos válidos.")

    # Análisis de profiles_to_scan.json
    print("\n--- Análisis de Perfiles ---")
    if df_profiles:
        analizar_profiles.contar_perfiles(df_profiles)
        analizar_profiles.analizar_origenes(df_profiles)
        analizar_profiles.analizar_fechas_creacion(df_profiles)
        analizar_profiles.analizar_descripciones(df_profiles)
        analizar_profiles.analizar_verificaciones(df_profiles)

    # Detener la SparkSession
    spark.stop()

if __name__ == "__main__":
    main()
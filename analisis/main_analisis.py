import os
import sys
from datetime import datetime

# Configurar UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configurar Python para PySpark en Windows
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
os.environ['PYSPARK_PYTHON'] = sys.executable

# Configurar Java 17 para PySpark (en lugar de Java 8)
os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-17'

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, explode, count, avg, min, max, stddev, 
    expr, to_date, hour, dayofweek, length, when,
    year, month, quarter, countDistinct, trim, split
)
from carga_datos import CargaDatos
from analizar_post import AnalizarPost
from analizar_profiles import AnalizarProfiles


# ═══════════════════════════════════════════════════════════
# FUNCIONES HELPER PARA FORMATO
# ═══════════════════════════════════════════════════════════

def print_banner(text):
    """Imprime un banner principal con el texto centrado"""
    width = 100
    print("\n" + "═" * width)
    print(f"  {text.upper()}")
    print("═" * width + "\n")


def print_section(number, title):
    """Imprime un separador de sección numerada"""
    width = 100
    print("\n" + "━" * width)
    print(f"{number}. {title.upper()}")
    print("━" * width + "\n")


def print_subsection(title):
    """Imprime un subseparador"""
    print(f"\n  {'─' * 80}")
    print(f"  {title}")
    print(f"  {'─' * 80}\n")


def print_metric(label, value, indent=2):
    """Imprime una métrica con formato"""
    spaces = " " * indent
    print(f"{spaces}• {label}: {value}")


def print_timestamp(label):
    """Imprime un timestamp formateado"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{label}] {now}")


# ═══════════════════════════════════════════════════════════
# FUNCIONES DE ANÁLISIS ADICIONALES
# ═══════════════════════════════════════════════════════════

def analizar_handles(df):
    """Analiza la distribución de handles por dominio"""
    try:
        print_subsection("2.3.1 Distribución de Handles por Dominio")
        
        # Extraer dominio del handle (después del último punto)
        df_handles = df.withColumn(
            "dominio", 
            expr("substring_index(handle, '.', -1)")
        )
        
        print("  Top 15 dominios más comunes:")
        df_handles.groupBy("dominio").count() \
            .orderBy(col("count").desc()) \
            .show(15, truncate=False)
        
        # Handles sin dominio bsky.social
        non_bsky = df_handles.filter(~col("handle").endswith(".bsky.social")).count()
        total = df.count()
        print_metric("Handles con dominio personalizado", f"{non_bsky} ({non_bsky/total*100:.1f}%)")
        
    except Exception as e:
        print(f"  ⚠️  Error al analizar handles: {e}")


def analizar_avatares(df):
    """Analiza la presencia de avatares"""
    try:
        print_subsection("2.3.2 Análisis de Avatares")
        
        con_avatar = df.filter(col("avatar").isNotNull() & (col("avatar") != "")).count()
        sin_avatar = df.filter(col("avatar").isNull() | (col("avatar") == "")).count()
        total = df.count()
        
        print_metric("Perfiles con avatar", f"{con_avatar} ({con_avatar/total*100:.1f}%)")
        print_metric("Perfiles sin avatar", f"{sin_avatar} ({sin_avatar/total*100:.1f}%)")
        
    except Exception as e:
        print(f"  ⚠️  Error al analizar avatares: {e}")


def analizar_display_names(df):
    """Analiza estadísticas de display names"""
    try:
        print_subsection("2.3.3 Análisis de Display Names")
        
        # Calcular longitud
        df_names = df.withColumn("longitud_nombre", length(col("display_name")))
        
        stats = df_names.select(
            min("longitud_nombre").alias("min"),
            max("longitud_nombre").alias("max"),
            avg("longitud_nombre").alias("avg")
        ).collect()[0]
        
        print_metric("Longitud mínima", stats["min"])
        print_metric("Longitud máxima", stats["max"])
        print_metric("Longitud promedio", f"{stats['avg']:.2f}")
        
        # Perfiles sin display name
        sin_nombre = df.filter(col("display_name").isNull() | (trim(col("display_name")) == "")).count()
        total = df.count()
        print_metric("Perfiles sin display name", f"{sin_nombre} ({sin_nombre/total*100:.1f}%)")
        
    except Exception as e:
        print(f"  ⚠️  Error al analizar display names: {e}")


def analizar_descripciones_detallado(df):
    """Análisis detallado de descripciones"""
    try:
        print_subsection("2.4.1 Estadísticas de Descripciones")
        
        # Calcular longitud
        df_desc = df.withColumn("longitud_descripcion", length(col("description")))
        
        stats = df_desc.select(
            min("longitud_descripcion").alias("min"),
            max("longitud_descripcion").alias("max"),
            avg("longitud_descripcion").alias("avg"),
            stddev("longitud_descripcion").alias("stddev")
        ).collect()[0]
        
        print_metric("Longitud mínima", stats["min"])
        print_metric("Longitud máxima", stats["max"])
        print_metric("Longitud promedio", f"{stats['avg']:.2f}")
        print_metric("Desviación estándar", f"{stats['stddev']:.2f}")
        
        # Perfiles con/sin descripción
        con_desc = df.filter(col("description").isNotNull() & (trim(col("description")) != "")).count()
        sin_desc = df.filter(col("description").isNull() | (trim(col("description")) == "")).count()
        total = df.count()
        
        print(f"\n  Distribución:")
        print_metric("Con descripción", f"{con_desc} ({con_desc/total*100:.1f}%)")
        print_metric("Sin descripción", f"{sin_desc} ({sin_desc/total*100:.1f}%)")
        
    except Exception as e:
        print(f"  ⚠️  Error al analizar descripciones: {e}")


def analizar_tendencias_temporales(df):
    """Analiza tendencias de crecimiento temporal"""
    try:
        print_subsection("2.2.4 Análisis por Trimestre")
        
        df_temporal = df.withColumn("fecha_creacion", to_date(col("created_at")))
        df_temporal = df_temporal.withColumn("trimestre", quarter(col("fecha_creacion")))
        df_temporal = df_temporal.withColumn("anio", year(col("fecha_creacion")))
        
        print("  Distribución por año y trimestre:")
        df_temporal.groupBy("anio", "trimestre") \
            .count() \
            .orderBy("anio", "trimestre") \
            .show(20, truncate=False)
        
    except Exception as e:
        print(f"  ⚠️  Error al analizar tendencias temporales: {e}")


def analizar_labels(df):
    """Analiza la distribución de labels"""
    try:
        print_subsection("2.5.2 Análisis de Labels")
        
        # Perfiles con/sin labels
        con_labels = df.filter(
            col("labels").isNotNull() & (expr("size(labels) > 0"))
        ).count()
        sin_labels = df.filter(
            col("labels").isNull() | (expr("size(labels) = 0"))
        ).count()
        total = df.count()
        
        print_metric("Perfiles con labels", f"{con_labels} ({con_labels/total*100:.1f}%)")
        print_metric("Perfiles sin labels", f"{sin_labels} ({sin_labels/total*100:.1f}%)")
        
        if con_labels > 0:
            print("\n  Extrayendo información de labels...")
            df_labels = df.filter(col("labels").isNotNull() & (expr("size(labels) > 0")))
            df_labels_exploded = df_labels.select(explode(col("labels")).alias("label"))
            
            print("\n  Top valores de labels (campo 'val'):")
            df_labels_exploded.select("label.val") \
                .groupBy("val") \
                .count() \
                .orderBy(col("count").desc()) \
                .show(10, truncate=False)
        
    except Exception as e:
        print(f"  ⚠️  Error al analizar labels: {e}")


def analizar_posts_detallado(df_posts_exploded):
    """Análisis detallado de posts"""
    try:
        if "post.text" not in df_posts_exploded.columns:
            print("  ⚠️  Columna 'post.text' no disponible")
            return
        
        print_subsection("3.3.1 Análisis de Contenido de Posts")
        
        # Longitud de posts
        df_text = df_posts_exploded.withColumn("longitud_post", length(col("post.text")))
        
        stats = df_text.select(
            min("longitud_post").alias("min"),
            max("longitud_post").alias("max"),
            avg("longitud_post").alias("avg"),
            stddev("longitud_post").alias("stddev")
        ).collect()[0]
        
        print("  Estadísticas de longitud:")
        print_metric("Longitud mínima", stats["min"])
        print_metric("Longitud máxima", stats["max"])
        print_metric("Longitud promedio", f"{stats['avg']:.2f} caracteres")
        print_metric("Desviación estándar", f"{stats['stddev']:.2f}")
        
    except Exception as e:
        print(f"  ⚠️  Error al analizar posts: {e}")


def analizar_posts_temporales(df_posts_exploded):
    """Análisis temporal de posts"""
    try:
        if "post.created_at" not in df_posts_exploded.columns:
            print("  ⚠️  Columna 'post.created_at' no disponible")
            return
        
        print_subsection("3.2.1 Distribución Temporal de Posts")
        
        df_temporal = df_posts_exploded.withColumn(
            "fecha_post", 
            to_date(col("post.created_at"))
        )
        
        # Por año/mes
        print("  Distribución por año:")
        df_temporal.groupBy(year(col("fecha_post")).alias("Año")) \
            .count() \
            .orderBy("Año") \
            .show(10, truncate=False)
        
        # Por hora del día
        df_hora = df_posts_exploded.withColumn(
            "hora", 
            hour(col("post.created_at"))
        )
        
        print("\n  Distribución por hora del día:")
        df_hora.groupBy("hora") \
            .count() \
            .orderBy("hora") \
            .show(24, truncate=False)
        
        # Por día de la semana (1=Domingo, 7=Sábado)
        df_dia = df_posts_exploded.withColumn(
            "dia_semana", 
            dayofweek(col("post.created_at"))
        )
        
        print("\n  Distribución por día de la semana (1=Domingo, 7=Sábado):")
        df_dia.groupBy("dia_semana") \
            .count() \
            .orderBy("dia_semana") \
            .show(7, truncate=False)
        
    except Exception as e:
        print(f"  ⚠️  Error al analizar temporalidad de posts: {e}")


def analizar_posts_por_usuario(df_posts, df_posts_exploded):
    """Analiza la distribución de posts por usuario"""
    try:
        print_subsection("3.1.1 Distribución de Posts por Usuario")
        
        # Contar posts por usuario
        posts_por_usuario = df_posts_exploded.groupBy("user_did") \
            .count() \
            .withColumnRenamed("count", "num_posts")
        
        stats = posts_por_usuario.select(
            min("num_posts").alias("min"),
            max("num_posts").alias("max"),
            avg("num_posts").alias("avg"),
            stddev("num_posts").alias("stddev")
        ).collect()[0]
        
        print_metric("Posts por usuario - Mínimo", stats["min"])
        print_metric("Posts por usuario - Máximo", stats["max"])
        print_metric("Posts por usuario - Promedio", f"{stats['avg']:.2f}")
        print_metric("Posts por usuario - Desviación estándar", f"{stats['stddev']:.2f}")
        
        print("\n  Top 10 usuarios con más posts:")
        posts_por_usuario.orderBy(col("num_posts").desc()) \
            .show(10, truncate=False)
        
    except Exception as e:
        print(f"  ⚠️  Error al analizar posts por usuario: {e}")


# ═══════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════

def main():
    inicio = datetime.now()
    
    # Banner principal
    print_banner("ANÁLISIS DESCRIPTIVO DE DATOS - BLUESKY")
    print_timestamp("Inicio del análisis")
    
    # Crear la SparkSession con configuración de memoria
    spark = SparkSession.builder \
        .appName("Bluesky Data Analysis") \
        .config("spark.driver.memory", "8g") \
        .config("spark.executor.memory", "8g") \
        .config("spark.sql.debug.maxToStringFields", "1000") \
        .getOrCreate()

    # Instanciar las clases
    carga_datos = CargaDatos(spark)
    analizar_post = AnalizarPost(spark)
    analizar_profiles = AnalizarProfiles(spark)

    # Rutas de los archivos JSON (relativas al script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    ruta_posts = os.path.join(base_dir, "almacen", "posts_usuarios.jsonl")
    ruta_profiles = os.path.join(base_dir, "almacen", "profiles_to_scan.json")

    # ─────────────────────────────────────────────────────────
    # CARGA DE DATOS
    # ─────────────────────────────────────────────────────────
    print("\n⏳ Cargando datos...")
    
    df_posts = carga_datos.cargar_posts_usuarios(ruta_posts)
    df_profiles = carga_datos.cargar_profiles_to_scan(ruta_profiles)

    # Manejar registros corruptos
    if df_posts:
        if "_corrupt_record" in df_posts.columns:
            df_posts = df_posts.filter(col("_corrupt_record").isNull())
        df_posts = df_posts.cache()

    if df_profiles:
        if "_corrupt_record" in df_profiles.columns:
            df_profiles = df_profiles.filter(col("_corrupt_record").isNull())
        df_profiles = df_profiles.cache()

    # Preparar datos de posts
    df_posts_exploded = None
    
    # DIAGNÓSTICO: Verificar estado de df_posts
    print("\n🔍 DIAGNÓSTICO DE POSTS:")
    if df_posts:
        print(f"  ✓ df_posts existe y tiene {df_posts.count()} registros (posts)")
        print(f"  ✓ Columnas disponibles: {df_posts.columns}")
        
        # El nuevo formato JSONL ya tiene cada post en una línea separada
        # Las columnas deberían ser: usuario_did, usuario_handle, cid, uri, createdAt, text, etc.
        if "usuario_did" in df_posts.columns:
            print("  ✓ Formato JSONL correcto detectado (un post por línea)")
            # Los posts ya están "exploded", cada fila es un post
            df_posts_exploded = df_posts
            
            # Renombrar usuario_did a user_did para compatibilidad con el código existente
            if "usuario_did" in df_posts_exploded.columns and "user_did" not in df_posts_exploded.columns:
                df_posts_exploded = df_posts_exploded.withColumnRenamed("usuario_did", "user_did")
            
            # Crear estructura "post" para compatibilidad con funciones de análisis existentes
            # que esperan columnas como "post.text", "post.created_at", etc.
            df_posts_exploded = df_posts_exploded.selectExpr(
                "user_did",
                "usuario_handle",
                "struct(cid, uri, createdAt as created_at, text, replyCount, repostCount, likeCount, hasEmbed) as post"
            )
            
            total_posts = df_posts_exploded.count()
            print(f"  ✓ Posts procesados exitosamente: {total_posts} posts")
        else:
            print("  ⚠️  Formato JSONL inesperado - columna 'usuario_did' no encontrada")
    else:
        print("  ✗ df_posts es None o está vacío")

    # ═══════════════════════════════════════════════════════════
    # 01. RESUMEN EJECUTIVO
    # ═══════════════════════════════════════════════════════════
    
    print_section("01", "RESUMEN EJECUTIVO")
    
    total_perfiles = df_profiles.count() if df_profiles else 0
    total_posts = df_posts_exploded.count() if df_posts_exploded else 0
    
    print_metric("Total de perfiles analizados", f"{total_perfiles:,}")
    print_metric("Total de posts analizados", f"{total_posts:,}")
    
    if df_profiles:
        # Periodo de datos
        try:
            df_temp = df_profiles.withColumn("fecha", to_date(col("created_at")))
            rango = df_temp.select(
                min("fecha").alias("min"), 
                max("fecha").alias("max")
            ).collect()[0]
            print_metric("Periodo de creación de perfiles", f"{rango['min']} a {rango['max']}")
        except:
            pass
        
        # Categoría principal
        try:
            cat_principal = df_profiles.groupBy("origen_categoria") \
                .count() \
                .orderBy(col("count").desc()) \
                .first()
            if cat_principal and cat_principal["origen_categoria"]:
                print_metric("Categoría principal", 
                           f"{cat_principal['origen_categoria']} ({cat_principal['count']:,} perfiles)")
        except:
            pass

    # ═══════════════════════════════════════════════════════════
    # 02. ANÁLISIS DE PERFILES
    # ═══════════════════════════════════════════════════════════
    
    print_section("02", "ANÁLISIS DE PERFILES")
    
    if df_profiles:
        # 2.1 Distribución por Origen
        print_subsection("2.1 Distribución por Origen")
        analizar_profiles.analizar_origenes(df_profiles)
        
        # 2.2 Análisis Temporal
        print_subsection("2.2 Análisis Temporal")
        analizar_profiles.analizar_fechas_creacion(df_profiles)
        analizar_tendencias_temporales(df_profiles)
        
        # 2.3 Análisis de Identidad
        print_subsection("2.3 Análisis de Identidad")
        analizar_handles(df_profiles)
        analizar_avatares(df_profiles)
        analizar_display_names(df_profiles)
        
        # 2.4 Análisis de Descripciones
        print_subsection("2.4 Análisis de Descripciones")
        analizar_descripciones_detallado(df_profiles)
        
        # 2.5 Verificaciones y Labels
        print_subsection("2.5 Verificaciones y Labels")
        print_subsection("2.5.1 Estado de Verificación")
        analizar_profiles.analizar_verificaciones(df_profiles)
        analizar_labels(df_profiles)
    else:
        print("  ⚠️  No hay datos de perfiles disponibles")

    # ═══════════════════════════════════════════════════════════
    # 03. ANÁLISIS DE PUBLICACIONES
    # ═══════════════════════════════════════════════════════════
    
    print_section("03", "ANÁLISIS DE PUBLICACIONES")
    
    if df_posts_exploded and df_posts_exploded.count() > 0:
        # 3.1 Métricas Generales
        print_subsection("3.1 Métricas Generales")
        analizar_post.contar_registros(df_posts_exploded)
        analizar_posts_por_usuario(df_posts_exploded, df_posts_exploded)
        
        # 3.2 Análisis Temporal
        print_subsection("3.2 Análisis Temporal")
        analizar_posts_temporales(df_posts_exploded)
        
        # 3.3 Análisis de Contenido
        print_subsection("3.3 Análisis de Contenido")
        analizar_posts_detallado(df_posts_exploded)
    else:
        print("  ⚠️  No hay datos de posts disponibles o no se pudieron extraer")

    # ═══════════════════════════════════════════════════════════
    # 04. INSIGHTS Y CONCLUSIONES
    # ═══════════════════════════════════════════════════════════
    
    print_section("04", "INSIGHTS Y CONCLUSIONES")
    
    print("  Resumen de hallazgos principales:\n")
    print_metric("Total de perfiles analizados", f"{total_perfiles:,}")
    print_metric("Total de publicaciones analizadas", f"{total_posts:,}")
    
    if total_perfiles > 0 and total_posts > 0:
        promedio_posts = total_posts / total_perfiles
        print_metric("Promedio de posts por perfil", f"{promedio_posts:.2f}")
    
    # Calcular tiempo de ejecución
    fin = datetime.now()
    duracion = (fin - inicio).total_seconds()
    
    print_timestamp("Finalización del análisis")
    print(f"\n⏱️  Tiempo total de ejecución: {duracion:.2f} segundos\n")
    
    print("═" * 100)
    print("  FIN DEL ANÁLISIS")
    print("═" * 100 + "\n")

    # Detener la SparkSession
    spark.stop()


if __name__ == "__main__":
    main()
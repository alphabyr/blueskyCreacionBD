# 📘 Guía Completa de Scripts del Proyecto Bluesky

Este documento detalla cada script del proyecto, organizado por módulos, explicando su función principal y cómo contribuye al sistema global. Ideal para entender el flujo completo del proyecto.

---

## 1. 📂 Módulo: Analisis (`analisis/`)
*Objetivo: Procesar datos masivos con PySpark y generar visualizaciones.*

### 📄 `main_analisis.py`
- **Qué hace**: Es el **cerebro del análisis**. Orquesta la lectura de datos, procesamiento y generación de reportes.
- **Flujo**: Inicializa Spark -> Carga perfiles y posts -> Ejecuta análisis descriptivos (conteo, medias, tops) -> Llama al exportador de Markdown.

### 📄 `generar_graficos.py`
- **Qué hace**: Genera **visualizaciones visuales** (imágenes .png) a partir de los datos procesados.
- **Detalle**: Crea 25-30 gráficos distintos (histogramas de seguidores, evolución temporal, distribución de likes, mapas de calor hora/día) usando `matplotlib` y `seaborn`.

### 📄 `carga_datos.py`
- **Qué hace**: Módulo utilitario para **leer los archivos JSON**.
- **Detalle**: Define esquemas estrictos de PySpark para leer `profiles_to_scan.json` y `posts_usuarios.json` correctamente, manejando estructuras anidadas complejas.

### 📄 `analizar_profiles.py`
- **Qué hace**: Contiene la lógica específica para **analizar usuarios**.
- **Detalle**: Calcula métricas como promedio de seguidores, antigüedad de cuentas, ratios follow/follower y detecta valores atípicos en perfiles.

### 📄 `analizar_post.py`
- **Qué hace**: Contiene la lógica específica para **analizar publicaciones**.
- **Detalle**: Analiza longitud de textos, frecuencia de palabras, hashtags más usados y patrones de actividad temporal.

### 📄 `exportador_markdown.py`
- **Qué hace**: Toma los resultados numéricos de Spark y **escribe el reporte final** (`analisis_descriptivo.md`).
- **Detalle**: Convierte DataFrames de Spark en tablas Markdown formateadas y organiza el texto del reporte.

### 📄 `spark_utils.py`
- **Qué hace**: Configura la **sesión de Spark**.
- **Detalle**: Ajusta la memoria, drivers y configuraciones técnicas para que Spark corra eficientemente en tu máquina local.

---

## 2. 📂 Módulo: Configuracion (`configuracion/`)
*Objetivo: Centralizar parámetros y credenciales.*

### 📄 `load_config.py`
- **Qué hace**: Carga y valida la configuración del proyecto.
- **Detalle**: Lee `config.yaml` y asegúra que todas las rutas y credenciales necesarias existan antes de ejecutar cualquier script. Evita errores por "missing configuration".

### 📄 `config.yaml` (Archivo de configuración)
- **Qué es**: El "panel de control" del proyecto.
- **Detalle**: Define rutas de archivos, credenciales de API (ocultas), parámetros de scraping y configuración de modelos en un solo lugar.

---

## 3. 📂 Módulo: Prediccion (`prediccion/`)
*Objetivo: Detectar bots usando Machine Learning.*

### 📄 `scripts/1_etiquetar_datos.py`
- **Qué hace**: Genera un **dataset de entrenamiento** inicial.
- **Detalle**: Aplica reglas heurísticas (ej: "si tiene 0 seguidores y 5000 seguidos en 1 día = bot") para etiquetar automáticamente usuarios como `BOT` o `HUMAN`.

### 📄 `scripts/2_entrenar_modelo.py`
- **Qué hace**: Entrena el modelo de **Inteligencia Artificial (XGBoost)**.
- **Detalle**: Toma los datos etiquetados, aprende patrones matemáticos que diferencian bots de humanos y guarda el modelo entrenado (`modelo_xgboost.json`).

### 📄 `scripts/3_predecir.py`
- **Qué hace**: Usa el modelo entrenado para **clasificar nuevos usuarios**.
- **Detalle**: Tú le das un usuario (ej: `luckayy.bsky.social`), el script descarga sus datos en tiempo real, extrae sus características y el modelo decide: "¿Es bot o humano?" con un % de probabilidad.

---

## 4. 📂 Módulo: Prediccion - Archivos Generados (`prediccion/modelos/`)
*Objetivo: Archivos que "guardan" el cerebro de la IA.*

> **¿Qué es un archivo `.pkl`?**
> Es un archivo **Pickle** de Python. Imagina que entrenar la IA cuesta mucho tiempo y cálculos. Pickle nos permite "congelar" ese objeto (el cerebro entrenado) en un archivo binario para guardarlo en el disco.
> Cuando queremos usar la IA después, simplemente "descongelamos" (cargamos) este archivo y la IA vuelve a la vida tal cual estaba, sin tener que volver a entrenar.

### 📦 `bot_detector.pkl`
- **Qué es**: **El Modelo (Cerebro)**.
- **Detalle**: Contiene el algoritmo XGBoost ya entrenado con todas las reglas matemáticas que aprendió para diferenciar bots de humanos.

### 📦 `feature_scaler.pkl`
- **Qué es**: **La Escala**.
- **Detalle**: La IA trabaja mejor si todos los números son parecidos (ej: entre 0 y 1). Este archivo guarda la "regla de conversión" para transformar tus datos (ej: 5000 seguidores) a la escala que la IA entiende (ej: 0.85). Es vital para que la predicción sea correcta.

### 📦 `feature_columns.pkl`
- **Qué es**: **La Lista de Ingredientes**.
- **Detalle**: Una lista simple con los nombres de las columnas en el orden exacto que el modelo las espera (ej: ['seguidores', 'ratio', 'posts_diarios'...]). Si le pasamos los datos en otro orden, la IA se confundiría.

### 📊 `feature_importance.csv`
- **Qué es**: **Reporte de Importancia**.
- **Detalle**: Un Excel simple (CSV) que nos dice **qué métricas fueron más útiles** para la IA.

### 🧠 Diccionario de Características (Features)
Aquí tienes una explicación simple de qué significa cada número que ve la IA:

| Característica | ¿Qué es? | ¿Por qué importa? |
|----------------|----------|-------------------|
| **avg_engagement** | Promedio de Likes+Respuestas recibidos | Los humanos suelen recibir feedback; los bots suelen ser ignorados. |
| **account_age_days** | Días que la cuenta lleva creada | Bots suelen ser cuentas recién creadas; humanos tienen historia. |
| **post_interval_std** | "Irregularidad" al publicar | Humanos somos caóticos (publicamos a horas raras); bots son robóticos/exactos. |
| **followers_ratio** | Seguidores divididos por Seguidos | Humanos famosos tienen ratio alto; bots tienen ratio bajo (siguen a miles para que les sigan). |
| **bio_length** | Longitud de la descripción | Bots suelen tener bios vacías o genéricas; humanos las personalizan más. |
| **avg_post_length** | Longitud promedio de los textos | Bots a veces spamean frases cortas; humanos escriben variado. |
| **std_post_length** | Variedad en la longitud de textos | Si siempre escribe mensajes de 50 letras exactas, huele a robot. |
| **vocabulary_diversity** | Riqueza de vocabulario | ¿Usa siempre las mismas 5 palabras? (Bot) ¿O usa muchas palabras distintas? (Humano). |
| **post_similarity_avg** | Repetición de contenido | Si sus posts son todos iguales ("Click aquí", "Click aquí"), es alto (Bot). |
| **night_posts_ratio** | % de posts hechos de madrugada | Los humanos dormimos; los bots pueden publicar 24/7 sin parar. |
| **url_ratio** | % de posts que son solo enlaces | Bots de spam solo ponen links; humanos hablan y opinan. |
| **handle_has_many_numbers** | Números en el nombre de usuario | `juan192837` suele ser bot generado auto; `juan_garcia` es más humano. |
| **has_avatar** | ¿Tiene foto de perfil? | 1 = Sí, 0 = No. Bots masivos a veces no tienen foto. |
| **repost_ratio** | % de posts que son Reposts (RT para otros) | Bots a veces solo amplifican a otros ("RT masivo") sin crear contenido. |

---

## 5. 📂 Módulo: Seguridad (`seguridad/`)
*Objetivo: Proteger el código y los datos.*

### 📄 `secure_file_handler.py`
- **Qué hace**: Manejo seguro de archivos.
- **Detalle**: Previene ataques de **Path Traversal** (intentar leer archivos fuera del proyecto como `C:/Windows/...`) validando estrictamente todas las rutas de archivo.

### 📄 `secure_model_handler.py`
- **Qué hace**: Carga segura de modelos ML.
- **Detalle**: Evita ataques de **Pickle Deserialization** (ejecución de código malicioso al cargar un modelo) usando formatos seguros (JSON) o validando checksums.

---

## 6. 📂 Módulo: Usuarios (`usuarios/`)
*Objetivo: Recolección de datos (Scraping).*

### 📄 `info.py`
- **Qué hace**: Extrae la **información del perfil**.
- **Detalle**: Conecta a la API de Bluesky y descarga: descripción, avatar, fechas de creación, contadores de seguidores/seguidos.

### 📄 `post.py`
- **Qué hace**: Extrae las **publicaciones del usuario**.
- **Detalle**: Descarga el historial de posts de un usuario, manejando paginación (para traer miles de posts) y guardándolos en formato JSON estructurado.

---

## 7. 🏠 Scripts Raíz (`/`, `Main/`, `gestor/`)

### 📄 `verificar_seguridad.py`
- **Qué hace**: Auditoría de seguridad.
- **Detalle**: Un script de diagnóstico que revisa si el sistema cumple con las normas de seguridad (permisos de archivos, existencia de carpetas seguras, integridad de modelos).

### 📄 `Main/main.py`
- **Qué hace**: El **punto de entrada principal** para la recolección de datos.
- **Detalle**: Coordina el uso de `usuarios/info.py` y `usuarios/post.py` para escanear listas masivas de usuarios (dadas en `profiles_to_scan.json`) y construir la base de datos (`almacen/`).

### 📄 `gestor/gestor_bluesky.py`
- **Qué hace**: Utilidad de gestión de la API.
- **Detalle**: Maneja la conexión pura con Bluesky, gestión de tokens de sesión y límites de velocidad (rate limits) para no ser bloqueados por la API.

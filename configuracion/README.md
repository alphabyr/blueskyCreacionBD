# ⚙️ Configuración del Proyecto

Sistema de configuración centralizado para todo el proyecto Bluesky.

## 📋 Descripción

Esta carpeta contiene todos los archivos de configuración centralizados del proyecto. Todos los scripts Python leen automáticamente desde `config.yaml` - **no necesitas modificar código Python** para cambiar parámetros.

---

## 🗂️ Archivos

### `config.yaml` ⭐ **PRINCIPAL**

Archivo de configuración centralizado con todos los parámetros modificables:

**Secciones**:
- **Rutas**: Ubicación de archivos de datos
- **Scraping**: Parámetros de extracción de perfiles y seguidores
- **Posts**: Configuración de obtención de posts
- **Spark**: Configuración de memoria y rendimiento PySpark
- **Análisis**: Parámetros de visualización
- **Modelo**: Parámetros de XGBoost y detección de bots
- **Heurísticas**: Reglas de etiquetado automático
- **Predicción**: Usuario objetivo y configuración de predicción

### `load_config.py`

Módulo Python para cargar y acceder a la configuración desde `config.yaml`.

**Patrón Singleton**: Garantiza que todos los scripts usen la misma instancia de configuración.

### `contraseñas.properties`

Archivo para credenciales de Bluesky (NO subir a Git, está en `.gitignore`).

---

## 🚀 Uso

### En Scripts Python

```python
from configuracion.load_config import config

# Método 1: Acceso directo
valor = config.get('seccion', 'parametro')

# Método 2: Métodos helper
usuarios = config.get_usuarios_por_semilla()
ruta = config.get_ruta_profiles()
spark_conf = config.get_spark_config()
```

### Modificar Configuración

1. Abre `config.yaml` en tu editor
2. Modifica los valores que necesites
3. Guarda el archivo
4. Los scripts leerán automáticamente la nueva configuración

**¡No necesitas modificar ningún archivo Python!**

---

## ⚙️ Parámetros Principales

### Credenciales Bluesky

Configura como variables de entorno (Windows PowerShell):

```powershell
$env:BSKY_HANDLE = "tu_usuario.bsky.social"
$env:BSKY_APP_PASSWORD = "xxxx-xxxx-xxxx-xxxx"
```

**Generar App Password**:
1. Inicia sesión en [Bluesky Web](https://bsky.app)
2. Ve a **Settings** → **Security** → **App Passwords**
3. Genera una nueva contraseña

### Memoria de Spark

Si tienes problemas de memoria (`OutOfMemoryError`):

```yaml
spark:
  driver_memory: "16g"      # Aumentar de 8g a 16g
  executor_memory: "16g"
  java_home: "C:\\Program Files\\Java\\jdk-17"
```

**Requisito**: Necesitas Java 17 para PySpark.

### Scraping

Para obtener más usuarios:

```yaml
scraping:
  usuarios_por_semilla: 50  # Default: 10
  pool_size: 100            # Default: 12
  page_limit: 100           # Default: 100
```

### Posts

Controlar límites y delays:

```yaml
posts:
  posts_por_usuario_limite: 50  # Default: 25
  delay_entre_requests: 1       # Segundos entre usuarios
  delay_rate_limit: 60          # Espera al encontrar rate limit
```

**Nota**: Si recibes muchos `RateLimitExceeded`, aumenta `delay_entre_requests` a 2-3 segundos.

### Análisis

Configurar visualización de resultados:

```yaml
analisis:
  top_n_resultados: 10      # Top N usuarios/posts a mostrar
  filas_mostrar: 15         # Filas en tablas de Spark
  truncar_tablas: 50        # Truncar texto largo
```

### Modelo de Detección de Bots

```yaml
modelo:
  xgboost:
    n_estimators: 100       # Número de árboles
    max_depth: 6            # Profundidad máxima
    learning_rate: 0.1      # Tasa de aprendizaje
  
  threshold_bot: 0.7        # Umbral de clasificación (0-1)
                            # Más alto = más estricto
```

### Heurísticas de Etiquetado

```yaml
heuristicas:
  min_reglas_bot: 3         # Mín. reglas para etiquetar como bot
  min_reglas_humano: 3      # Mín. reglas para etiquetar como humano
```

### Predicción

```yaml
prediccion:
  target_handle: "usuario.bsky.social"  # Handle a analizar
  target_did: ""                        # O DID
  num_posts_analizar: 25                # Posts a obtener
  mostrar_features: true                # Mostrar todos los features
  mostrar_top_factores: 5               # Top N factores más importantes
```

---

## 🔧 Configuración por Caso de Uso

### Caso 1: Scraping Intensivo

```yaml
scraping:
  usuarios_por_semilla: 100
  pool_size: 50

posts:
  posts_por_usuario_limite: 100
  delay_entre_requests: 2  # Más conservador para evitar rate limits
```

### Caso 2: Análisis con Datos Grandes

```yaml
spark:
  driver_memory: "16g"
  executor_memory: "16g"
  max_to_string_fields: 2000

analisis:
  top_n_resultados: 20
  filas_mostrar: 30
```

### Caso 3: Detección de Bots Conservadora

```yaml
modelo:
  threshold_bot: 0.8      # Más estricto (menos falsos positivos)

heuristicas:
  min_reglas_bot: 4       # Más reglas requeridas
```

### Caso 4: Detección de Bots Agresiva

```yaml
modelo:
  threshold_bot: 0.6      # Más sensible (detecta más bots)

heuristicas:
  min_reglas_bot: 2       # Menos reglas requeridas
```

---

## ✅ Validación

Verificar que la configuración se carga correctamente:

```bash
python -c "from configuracion.load_config import config; print('✓ Configuración OK')"
```

Ver un valor específico:

```bash
python -c "from configuracion.load_config import config; print(config.get('spark', 'driver_memory'))"
```

---

## 📊 Parámetros Configurables Completos

### Rutas
- `directorio_almacen`: Carpeta de datos
- `archivo_profiles`: JSON de perfiles
- `archivo_posts_json`: JSON de posts
- `archivo_posts_jsonl`: JSONL de posts (para Spark)

### Scraping
- `usuarios_por_semilla`: Usuarios a obtener por cuenta semilla
- `pool_size`: Tamaño del pool de threads
- `page_limit`: Límite de páginas por petición

### Posts
- `posts_por_usuario_limite`: Posts max por usuario
- `delay_entre_requests`: Delay entre requests (seg)
- `delay_rate_limit`: Delay al encontrar rate limit (seg)

### Spark
- `app_name`: Nombre de la aplicación Spark
- `driver_memory`: Memoria del driver
- `executor_memory`: Memoria del executor
- `max_to_string_fields`: Max fields para toString
- `java_home`: Ruta de Java 17

### Análisis
- `top_n_resultados`: Top N en rankings
- `filas_mostrar`: Filas en show()
- `truncar_tablas`: Truncado de texto

### Conversión
- `intervalo_progreso`: Intervalo de log de progreso
- `encoding`: Encoding de archivos

---

## 🛠️ Troubleshooting

### Variables de Entorno No Reconocidas

**Causa**: Las variables de entorno solo duran la sesión actual de PowerShell.

**Solución**: Configura las variables en cada sesión, o hazlas permanentes:
1. Busca "Variables de entorno" en Windows
2. Añade `BSKY_HANDLE` y `BSKY_APP_PASSWORD` como variables de usuario

### Error al Cargar config.yaml

**Causa**: Ruta incorrecta o sintaxis YAML inválida.

**Solución**: 
- Verifica que `config.yaml` esté en la carpeta `configuracion/`
- Valida la sintaxis YAML (indentación correcta)

### Java No Encontrado

**Causa**: `java_home` incorrecto en `config.yaml`.

**Solución**: Verifica la ruta de Java 17:
```powershell
dir "C:\Program Files\Java\"
```

Actualiza en `config.yaml`:
```yaml
spark:
  java_home: "C:\\Program Files\\Java\\jdk-17"  # Usar \\ en Windows
```

---

## 📚 Documentación Relacionada

- **Proyecto general**: [`../README.md`](../README.md)
- **Análisis**: [`../analisis/README.md`](../analisis/README.md)
- **Predicción**: [`../prediccion/README.md`](../prediccion/README.md)

---

## 📝 Notas Adicionales

### Beneficios de la Configuración Centralizada

1. **Centralización**: Todos los parámetros en un solo lugar
2. **Facilidad**: Cambiar configuración sin tocar código Python
3. **Documentación**: El YAML es auto-documentado con comentarios
4. **Validación**: Patrón Singleton asegura consistencia
5. **Mantenibilidad**: Más fácil gestionar configuraciones complejas

### Archivos que Usan esta Configuración

- `Main/main.py`
- `usuarios/info.py`
- `usuarios/post.py`
- `analisis/main_analisis.py`
- `prediccion/scripts/*.py`

Todos estos scripts importan y usan `config` automáticamente.

---

¿Preguntas? Revisa el código fuente en `load_config.py` o abre `config.yaml` para ver todos los parámetros disponibles.

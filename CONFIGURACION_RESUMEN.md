# Resumen de Configuración Centralizada

## ✅ Archivos Creados

1. **`configuracion/config.yaml`** - Configuración centralizada
2. **`configuracion/load_config.py`** - Módulo para cargar la configuración
3. **`configuracion/README.md`** - Documentación

## ✅ Archivos Modificados

1. **`Main/main.py`**
   - ✅ Importa `config`
   - ✅ Usa `config.get_usuarios_por_semilla()`
   - ✅ Usa `config.get_pool_size()`
   - ✅ Usa `config.get_page_limit()`
   - ✅ Usa `config.get_posts_por_usuario_limite()`
   - ✅ Usa `config.get_ruta_profiles()`

2. **`usuarios/post.py`**
   - ✅ Importa `config`
   - ✅ Usa `config.get_ruta_profiles()`
   - ✅ Usa `config.get_ruta_posts_json()`
   - ✅ Usa `config.get_posts_por_usuario_limite()`
   - ✅ Usa `config.get_delay_entre_requests()`
   - ✅ Usa `config.get_delay_rate_limit()`

3. **`analisis/main_analisis.py`**
   - ✅ Importa `config`
   - ✅ Usa `config.get_java_home()`
   - ✅ Usa `config.get_spark_config()` para todas las opciones de Spark
   - ✅ Usa `config.get_ruta_posts_jsonl()`
   - ✅ Usa `config.get_ruta_profiles()`

4. **`hacer.md`**
   - ✅ Actualizado con sección de configuración YAML

## 📋 Parámetros Configurables

### Rutas
- `directorio_almacen`: "almacen"
- `archivo_profiles`: "profiles_to_scan.json"
- `archivo_posts_json`: "posts_usuarios.json"
- `archivo_posts_jsonl`: "posts_usuarios.jsonl"

### Scraping
- `usuarios_por_semilla`: 10
- `pool_size`: 12
- `page_limit`: 100

### Posts
- `posts_por_usuario_limite`: 25
- `delay_entre_requests`: 1
- `delay_rate_limit`: 60

### Spark
- `app_name`: "Bluesky Data Analysis"
- `driver_memory`: "8g"
- `executor_memory`: "8g"
- `max_to_string_fields`: 1000
- `java_home`: "C:\\Program Files\\Java\\jdk-17"

### Análisis
- `top_n_resultados`: 10
- `filas_mostrar`: 15
- `truncar_tablas`: 50

### Conversión
- `intervalo_progreso`: 1000
- `encoding`: "utf-8"

## 🔧 Cómo Usar

Para acceder a cualquier valor de configuración en tu código:

```python
from configuracion.load_config import config

# Método 1: Acceso directo
valor = config.get('seccion', 'parametro')

# Método 2: Métodos helper
usuarios = config.get_usuarios_por_semilla()
ruta = config.get_ruta_profiles()
spark_conf = config.get_spark_config()
```

## ✅ Beneficios

1. **Centralización**: Todos los parámetros en un solo lugar
2. **Facilidad**: Cambiar configuración sin tocar código Python
3. **Documentación**: El YAML es auto-documentado con comentarios
4. **Validación**: Patrón Singleton asegura consistencia
5. **Mantenibilidad**: Más fácil gestionar configuraciones complejas

## 🧪 Test

```bash
python -c "from configuracion.load_config import config; print('✓ Config OK')"
```

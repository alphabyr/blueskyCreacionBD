# Configuración del Proyecto

Esta carpeta contiene todos los archivos de configuración centralizados del proyecto Bluesky.

## Archivos

### `config.yaml` ⭐ **PRINCIPAL**

Archivo de configuración centralizado con todos los parámetros modificables del proyecto:

- **Rutas**: Ubicación de archivos de datos
- **Scraping**: Parámetros de extracción de perfiles y seguidores
- **Posts**: Configuración de obtención de posts
- **Spark**: Configuración de memoria y rendimiento
- **Análisis**: Parámetros de visualización

**Uso**: Todos los scripts Python leen automáticamente desde este archivo.

### `load_config.py`

Módulo Python para cargar y acceder a la configuración desde `config.yaml`.

**Ejemplo de uso en otros scripts**:

```python
from configuracion.load_config import config

# Obtener valores
driver_memory = config.get('spark', 'driver_memory')
usuarios_por_semilla = config.get_usuarios_por_semilla()
ruta_profiles = config.get_ruta_profiles()
```

### `contraseñas.properties`

Archivo para credenciales de Bluesky (NO subir a Git).

### `config.md`

Documentación adicional sobre configuración.

## ¿Cómo modificar la configuración?

1. Abre `config.yaml`
2. Modifica los valores que necesites
3. Guarda el archivo
4. Los scripts leerán automáticamente la nueva configuración

**No necesitas modificar ningún archivo Python.**

## Parámetros Importantes

### Memoria de Spark

Si tienes problemas de memoria:

```yaml
spark:
  driver_memory: "16g"  # Aumentar de 8g a 16g
  executor_memory: "16g"
```

### Scraping más agresivo

Para obtener más usuarios:

```yaml
scraping:
  usuarios_por_semilla: 50  # De 10 a 50
  pool_size: 100  # De 12 a 100
```

### Más posts por usuario

```yaml
posts:
  posts_por_usuario_limite: 50  # De 25 a 50
```

### Rate Limits

Si recibes muchos rate limits:

```yaml
posts:
  delay_entre_requests: 2  # De 1 a 2 segundos
  delay_rate_limit: 120  # De 60 a 120 segundos
```

## Validación

Para verificar que la configuración se carga correctamente:

```bash
python -c "from configuracion.load_config import config; print('✓ OK')"
```

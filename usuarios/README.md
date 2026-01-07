# 👥 Módulo de Usuarios

Gestión de extracción de perfiles y publicaciones de usuarios de Bluesky.

## 📋 Descripción

Este módulo contiene las clases responsables de:
- Obtener perfiles de usuarios (seguidores)
- Extraer publicaciones de cada usuario
- Gestionar el progreso de extracción
- Guardar datos de forma incremental

---

## 🗂️ Archivos

### `info.py` - Extracción de Perfiles

**Clase**: `BlueskyFollowersFetcher`

**Funcionalidad**:
- Obtiene seguidores de una cuenta semilla
- Extrae información detallada del perfil
- Guarda perfiles en `almacen/profiles_to_scan.json`
- Evita duplicados mediante DID

**Datos extraídos por perfil**:
- Handle y DID (identificador único)
- Display name y descripción
- Fecha de creación
- Estado de verificación
- Conteo de seguidores/seguidos
- Avatar y banner
- Engagement (likes, posts, etc.)

### `post.py` - Extracción de Posts

**Clase**: `BlueskyPostsFetcher`

**Funcionalidad**:
- Lee perfiles desde `profiles_to_scan.json`
- Obtiene los últimos N posts de cada usuario
- Guarda posts en `almacen/posts_usuarios.json`
- **Reanudación automática**: Continúa desde donde se interrumpió

**Datos extraídos por post**:
- URI y CID del post
- Texto del post
- Fecha de creación
- Autor (DID y handle)
- Engagement (likes, reposts, replies)
- Idioma
- Menciones, URLs, hashtags

---

## 🚀 Uso

### Obtener Perfiles

```python
from usuarios.info import BlueskyFollowersFetcher

fetcher = BlueskyFollowersFetcher(
    handle="cuenta_semilla.bsky.social",
    app_password="xxxx-xxxx-xxxx-xxxx",
    output_file="almacen/profiles_to_scan.json",
    pool_size=12,
    page_limit=100
)
profiles = fetcher.fetch_followers("did:plc:seed_account")
```

### Obtener Posts

```python
from usuarios.post import BlueskyPostsFetcher

fetcher = BlueskyPostsFetcher(
    handle="tu_usuario.bsky.social",
    app_password="xxxx-xxxx-xxxx-xxxx",
    input_file="almacen/profiles_to_scan.json",
    output_file="almacen/posts_usuarios.json",
    posts_per_user_limit=25
)
fetcher.run()
```

**Nota**: El método `run()` procesará automáticamente todos los usuarios y guardará el progreso.

---

## ⚙️ Configuración

Ambas clases leen parámetros desde `configuracion/config.yaml`:

```yaml
scraping:
  usuarios_por_semilla: 10
  pool_size: 12
  page_limit: 100

posts:
  posts_por_usuario_limite: 25
  delay_entre_requests: 1        # Delay entre usuarios
  delay_rate_limit: 60           # Delay al encontrar rate limit

rutas:
  directorio_almacen: "almacen"
  archivo_profiles: "profiles_to_scan.json"
  archivo_posts_json: "posts_usuarios.json"
```

---

## 🔄 Reanudación Automática

### Cómo Funciona

El extractor de posts (`post.py`) implementa reanudación automática:

1. **Lee el progreso guardado** en `posts_usuarios.json`
2. **Carga los DIDs ya procesados**
3. **Procesa solo usuarios pendientes**
4. **Guarda progreso incrementalmente**

### Interrumpir y Reanudar

```bash
# Ejecutar extracción
python Main/main.py

# Presionar Ctrl+C para interrumpir

# Volver a ejecutar - continuará desde donde se quedó
python Main/main.py
```

---

## 🛡️ Seguridad

Ambos módulos utilizan `SecureFileHandler` del módulo de seguridad para:

- ✅ **Validación de rutas**: Previene path traversal
- ✅ **Permisos restrictivos**: Archivos creados con 0o600
- ✅ **Operaciones atómicas**: Previene TOCTOU
- ✅ **Manejo de excepciones**: Gestión robusta de errores

```python
from seguridad.secure_file_handler import SecureFileHandler

handler = SecureFileHandler('almacen')
with handler.abrir_escritura('profiles.json', permisos=0o600) as f:
    json.dump(data, f)
```

---

## 🔧 Manejo de Errores

### Rate Limiting

Si se detecta `RateLimitExceeded`:
- El script espera automáticamente 60 segundos (configurable)
- Luego continúa con el siguiente usuario
- El progreso se guarda antes de esperar

### Usuarios No Encontrados

Si un perfil no existe (`ActorNotFound`):
- Se registra el error
- Se salta al siguiente usuario
- No afecta al resto del proceso

### Errores de Red

En caso de error de conexión:
- Se reintenta automáticamente
- Si persiste, se registra y continúa
- El progreso se guarda regularmente

---

## 📊 Estadísticas de Progreso

Durante la ejecución, el script muestra:

```
Procesando 1234/14900: usuario.bsky.social (did:plc:abc123...)
Se obtuvieron 25 posts.
Progreso guardado.
```

---

## 🛠️ Troubleshooting

### Error: "Actor not found"

**Causa**: El usuario eliminó su cuenta o cambió su handle.

**Solución**: Normal, el script los salta automáticamente.

### Error: Rate limit exceeded

**Causa**: Demasiadas peticiones a la API de Bluesky.

**Solución**: 
- El script espera automáticamente
- Aumenta `delay_entre_requests` en config.yaml

### El script se cuelga

**Causa**: Puede ser un problema de red o API.

**Solución**:
- Presiona `Ctrl+C`
- Vuelve a ejecutar - continuará desde donde lo dejaste

---

## 📈 Optimización

### Scraping Más Rápido

**Advertencia**: Puede causar más rate limits

```yaml
posts:
  delay_entre_requests: 0.5      # Reducir a 0.5 segundos
```

### Scraping Más Seguro

```yaml
posts:
  delay_entre_requests: 2        # Aumentar a 2 segundos
  delay_rate_limit: 120          # Aumentar espera en rate limit
```

---

## 📚 Documentación Relacionada

- **Configuración**: [`../configuracion/README.md`](../configuracion/README.md)
- **Seguridad**: [`../seguridad/README.md`](../seguridad/README.md)
- **Proyecto general**: [`../README.md`](../README.md)

---

¿Preguntas? Revisa el código fuente en `info.py` y `post.py`.

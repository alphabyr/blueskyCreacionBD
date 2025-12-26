# Tareas Pendientes - Completar Scraping de Posts

## 📊 Situación Actual

- **14,900 perfiles** en `profiles_to_scan.json`
- **Solo 3,343 usuarios procesados** en `posts_usuarios.json` (22.4%)
- **~9,145 usuarios pendientes** de procesar (77.6%)
- **9,512 posts totales** obtenidos hasta ahora

El proceso de scraping se interrumpió. El archivo `posts_usuarios.json` está **incompleto**.

---

## ✅ Tareas para Completar Mañana

### 1. Continuar el Scraping de Posts

El script `Main/main.py` tiene reanudación automática. Solo necesitas ejecutarlo:

```bash
cd Main
python main.py
```

**IMPORTANTE**: 
- El script automáticamente detectará los 3,343 usuarios ya procesados
- Solo procesará los ~9,145 usuarios faltantes
- Esto tomará **varias horas** (~2-3 horas con delays de 1 seg/usuario)
- Puedes interrumpir con `Ctrl+C` y reanudará desde donde lo dejaste

### 2. Alternativa: Solo Ejecutar la Parte de Posts

Si NO quieres regenerar perfiles (que ya tienes), crea y ejecuta este script:

**Archivo: `Main/solo_posts.py`**
```python
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from usuarios.post import BlueskyPostsFetcher

# Configurar handle y contraseña
# Opción 1: Variables de entorno (recomendado)
# export BSKY_HANDLE="tu_handle.bsky.social"
# export BSKY_APP_PASSWORD="tu_app_password"

# Opción 2: Hardcodeado (menos seguro)
HANDLE = None  # O "tu_handle.bsky.social"
APP_PASSWORD = None  # O "tu_app_password"

if __name__ == "__main__":
    fetcher = BlueskyPostsFetcher(
        handle=HANDLE,
        app_password=APP_PASSWORD,
        input_file='profiles_to_scan.json',
        output_file='posts_usuarios.json',
        posts_per_user_limit=25
    )
    fetcher.run()
```

Luego ejecuta:
```bash
cd Main
python solo_posts.py
```

### 3. Monitorear el Progreso

Durante la ejecución, el script muestra:
- `Procesando X/9145: handle (did)`
- `Se obtuvieron X posts.`
- `Progreso guardado.`

Si se interrumpe, simplemente vuelve a ejecutar y continuará automáticamente.

### 4. Verificar Completitud

Una vez termine, verifica que todo esté completo:

```bash
cd analisis
python verificar_discrepancia.py
```

Debería mostrar:
- ✅ `Usuarios en posts pero NO en profiles: 0` (o muy pocos)
- ✅ Total de posts: mucho más que 9,512

### 5. Regenerar JSONL con Todos los Posts

Una vez completado el scraping:

```bash
cd analisis
python convertir_posts_correctamente.py
```

Esto actualizará `posts_usuarios.jsonl` con TODOS los posts.

### 6. Ejecutar Análisis Completo

```bash
python main_analisis.py
```

Ahora debería mostrar miles de posts más en el análisis.

### 7. Limpieza Final

Elimina archivos temporales:

```bash
cd analisis
Remove-Item contar_posts_real.py, verificar_discrepancia.py, convertir_posts_correctamente.py, investigar_estructura.py -ErrorAction SilentlyContinue
```

### 8. Commit Final

```bash
git add .
git commit -m "Scraping completo de posts - todos los usuarios procesados"
git push
```

---

## ⚙️ Configuración Centralizada (NUEVO)

**Todas las configuraciones del proyecto ahora se gestionan desde `configuracion/config.yaml`**

### Parámetros Configurables:

- **Spark**: Memoria driver/executor, nombre app, max fields
- **Rutas**: Nombres de archivos de entrada/salida
- **Scraping**: Usuarios por semilla, pool size, page limit
- **Posts**: Límite de posts por usuario, delays entre requests
- **Análisis**: Top N resultados, filas a mostrar, truncado

### Para modificar la configuración:

Edita `configuracion/config.yaml` y cambia los valores según necesites:

```yaml
scraping:
  usuarios_por_semilla: 10  # Cambiar según necesites
  pool_size: 12

posts:
  posts_por_usuario_limite: 25  # Aumentar si quieres más posts
  delay_entre_requests: 1  # Aumentar si hay rate limits

spark:
  driver_memory: "8g"  # Aumentar si tienes más RAM
  executor_memory: "8g"
```

**No necesitas modificar ningún archivo Python** - todos leen automáticamente desde el YAML.

---

## 🔧 Configuración de Credenciales

Si te falta configurar las credenciales para el scraping:

### Opción A: Variables de Entorno (Recomendado)

**Windows PowerShell:**
```powershell
$env:BSKY_HANDLE = "tu_handle.bsky.social"
$env:BSKY_APP_PASSWORD = "tu_app_password"
```

### Opción B: Archivo .env

Crea `.env` en la raíz del proyecto:
```
BSKY_HANDLE=tu_handle.bsky.social
BSKY_APP_PASSWORD=tu_app_password
```

### Opción C: Modificar main.py

En `Main/main.py` línea 125-127:
```python
if __name__ == "__main__":
    app = MainApp(
        bsky_handle="tu_handle.bsky.social",
        bsky_app_password="tu_app_password"
    )
    app.run()
```

---

## ⚠️ Problemas Comunes

### Rate Limit
Si ves `RateLimit exceeded`:
- El script automáticamente espera 60 segundos
- Déjalo continuar, se recuperará solo

### "Actor not found" / "Profile not found"
- Normal, algunos usuarios borran sus cuentas
- El script los salta automáticamente
- No afecta a los demás usuarios

### El script se cuelga
- Presiona `Ctrl+C` para interrumpir
- Vuelve a ejecutar, continuará desde donde lo dejaste

---

## 📈 Estimación de Tiempo

- **~9,145 usuarios pendientes**
- **1 segundo de delay por usuario** (para evitar rate limits)
- **Tiempo estimado**: ~2.5 horas (9145 seg = 152 min)
- Puede ser más si hay rate limits o errores de red

---

## ✅ Checklist Final

- [ ] Ejecutar scraping de posts faltantes (`main.py` o `solo_posts.py`)
- [ ] Verificar completitud con `verificar_discrepancia.py`
- [ ] Regenerar JSONL con `convertir_posts_correctamente.py`
- [ ] Ejecutar análisis completo con `main_analisis.py`
- [ ] Verificar que el análisis muestre miles de posts más
- [ ] Limpiar archivos temporales
- [ ] Commit y push
# 🔒 Módulo de Seguridad

Este módulo proporciona herramientas para el manejo seguro de archivos y modelos ML en el proyecto Bluesky.

## 📋 Componentes

### `SecureFileHandler`

Manejo seguro de archivos con prevención de ataques:

- **Path Traversal**: Valida que las rutas estén dentro del directorio permitido
- **Symlink Attacks**: Resuelve symlinks antes de validar
- **TOCTOU**: Usa operaciones atómicas para evitar race conditions
- **Permisos Restrictivos**: Crea archivos con permisos 0o600 (solo propietario)

**Uso:**

```python
from seguridad.secure_file_handler import SecureFileHandler

# Crear handler con directorio base
handler = SecureFileHandler('/ruta/al/proyecto/almacen')

# Leer archivo de forma segura
try:
    with handler.abrir_lectura('profiles_to_scan.json') as f:
        data = json.load(f)
except ValueError as e:
    print(f"Acceso denegado: {e}")

# Escribir archivo con permisos restrictivos
with handler.abrir_escritura('output.json', permisos=0o600) as f:
    json.dump(data, f)

# Esto será bloqueado:
try:
    with handler.abrir_lectura('../../../etc/passwd') as f:  # ❌
        pass
except ValueError:
    print("Ataque de path traversal bloqueado ✓")
```

### `SecureModelHandler`

Manejo seguro de modelos ML con verificación de integridad:

- **Checksums SHA-256**: Detecta modificaciones no autorizadas
- **Permisos Restrictivos**: Guarda modelos con permisos 0o600
- **Validación Automática**: Verifica integridad al cargar
- **Registro de Integridad**: Mantiene registro de checksums

**Uso:**

```python
from seguridad.secure_model_handler import SecureModelHandler

handler = SecureModelHandler('prediccion/modelos')

# Guardar modelo con checksum
handler.guardar_modelo(model, 'bot_detector.pkl', permisos=0o600)

# Cargar con verificación de integridad
try:
    model = handler.cargar_modelo('bot_detector.pkl', verificar_integridad=True)
except ValueError as e:
    print(f"⚠️ ALERTA: {e}")  # Archivo modificado

# Verificar todos los modelos
resultados = handler.verificar_todos()
for r in resultados:
    print(f"{r['estado']} {r['archivo']}: {r['mensaje']}")
```

## 🛡️ Vulnerabilidades Mitigadas

### 1. **Path Traversal (CWE-22)**
- **Antes**: `open("../../../etc/passwd")` permitido
- **Ahora**: Validación estricta de rutas, solo acceso dentro de directorio base

### 2. **Deserialización Insegura (CWE-502)**
- **Antes**: `pickle.load()` sin validación → RCE
- **Ahora**: Verificación de checksums SHA-256 antes de cargar

### 3. **TOCTOU Race Condition (CWE-367)**
- **Antes**: `os.path.exists()` → `open()` (ventana de ataque)
- **Ahora**: Operaciones atómicas con `os.open()`

### 4. **Permisos Inseguros (CWE-732)**
- **Antes**: Archivos creados con permisos por defecto (0o644)
- **Ahora**: Permisos restrictivos 0o600 (solo propietario)

### 5. **Symlink Attacks (CWE-59)**
- **Antes**: Seguía symlinks sin validar
- **Ahora**: Resuelve symlinks y valida destino final

## 🔍 Verificación de Seguridad

Ejecuta el script de auditoría:

```bash
python verificar_seguridad.py
```

Este script verifica:
- ✅ Integridad de modelos ML (checksums)
- ✅ Permisos de archivos sensibles
- ✅ Listado de modelos con sus hashes

## 📊 Impacto de Seguridad

| Vulnerabilidad | Antes | Después | Mitigación |
|----------------|-------|---------|------------|
| Path Traversal | 🔴 CRÍTICO | ✅ MITIGADO | Validación de rutas |
| Pickle RCE | 🔴 CRÍTICO | ✅ MITIGADO | Checksums SHA-256 |
| TOCTOU | 🟠 ALTO | ✅ MITIGADO | Operaciones atómicas |
| Permisos | 🟡 MEDIO | ✅ MITIGADO | Permisos 0o600 |
| Symlinks | 🟡 MEDIO | ✅ MITIGADO | Resolución segura |

## 🔧 Mantenimiento

### Regenerar Checksums

Si modificas los modelos legítimamente:

```bash
cd prediccion
python scripts/2_entrenar_modelo.py  # Regenera checksums automáticamente
```

### Limpiar Modelos Comprometidos

Si sospechas que los modelos fueron modificados:

```bash
rm -rf prediccion/modelos/
python prediccion/scripts/2_entrenar_modelo.py
```

### Verificar Permisos

```bash
# Verificar permisos de archivos sensibles
ls -la almacen/*.json prediccion/modelos/*.pkl

# Corregir permisos si es necesario
chmod 600 almacen/*.json prediccion/modelos/*.pkl
```

## 🚨 Respuesta a Incidentes

Si `verificar_seguridad.py` reporta archivos modificados:

1. **NO uses los modelos** - Pueden contener código malicioso
2. **Revisa los logs** - Busca accesos no autorizados
3. **Elimina los modelos** - `rm -rf prediccion/modelos/`
4. **Reentrena desde cero** - `python scripts/2_entrenar_modelo.py`
5. **Revisa el código fuente** - Busca modificaciones sospechosas
6. **Cambia credenciales** - Si usabas claves de API

## 📚 Referencias

- [CWE-22: Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
- [CWE-502: Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html)
- [CWE-367: Time-of-check Time-of-use (TOCTOU)](https://cwe.mitre.org/data/definitions/367.html)
- [OWASP: Insecure Deserialization](https://owasp.org/www-project-top-ten/2017/A8_2017-Insecure_Deserialization)

# REPORTE DE SEGURIDAD 🔒

Este documento resume las medidas de seguridad implementadas en el proyecto *BlueskyCreacionBD*.

Cada entrada sigue la estructura solicitada:
- **Clase/Función**
- **Descripción**
- **Justificación**

---

## 1) `seguridad.SecureFileHandler` (clase) ✅

**Descripción:**
- Handler para operaciones seguras con archivos.
- Métodos principales:
  - `validar_ruta(ruta)`: normaliza y resuelve rutas, comprueba que la ruta esté dentro de `base_dir` usando `Path.resolve()` y `relative_to()` para evitar path traversal y ataques vía symlink.
  - `abrir_lectura(...)`: valida ruta, verifica existencia y que sea archivo regular antes de abrir.
  - `abrir_escritura(...)`: valida ruta, crea directorios padres con modo `0o700`, abre fichero con `os.open(..., permisos)` para aplicar permisos restrictivos (por defecto `0o600`) y mitigar TOCTOU.
  - `existe`, `es_archivo`: wrappers seguros para comprobaciones.

**Justificación:**
- Previene path traversal, accesos fuera del directorio permitido y ataques basados en symlinks.
- Garantiza permisos restrictivos y reduce la ventana de race conditions usando descriptores de archivo.

---

## 2) `seguridad.SecureModelHandler` (clase) ✅

**Descripción:**
- Gestión segura de modelos ML en disco.
- Funcionalidades:
  - `calcular_checksum(archivo)`: SHA-256 para archivos.
  - `guardar_modelo(modelo, nombre_archivo, permisos)`: serializa (pickle) y guarda con permisos `0o600`, registra checksum en `checksums.json`.
  - `cargar_modelo(nombre_archivo, verificar_integridad=True)`: verifica checksum antes de `pickle.load`; rechaza la carga si el checksum no coincide.
  - Métodos auxiliares: `_guardar_checksum`, `_obtener_checksum`, `_cargar_checksums`, `listar_modelos`, `verificar_todos`.

**Justificación:**
- Mitiga riesgo de RCE por deserialización de Pickle al asegurar que sólo se carguen archivos con checksum conocido; detecta alteraciones y evita cargar modelos modificados.
- Uso de permisos restrictivos reduce exposición de archivos sensibles.

---

## 3) `gestor.ConexionBluesky` (clase) ✅

**Descripción:**
- Manejo de credenciales y sesión con la API de Bluesky.
- Lee `BSKY_HANDLE` y `BSKY_APP_PASSWORD` desde variables de entorno si no se pasan explícitamente; lanza error si faltan credenciales; centraliza login y re-autenticación (`conectar`, `get_client`).

**Justificación:**
- Evita hardcoding de credenciales en el código; promueve el uso de variables de entorno (mejor práctica para secret management) y centraliza el manejo de autenticación.

---

## 4) `usuarios.datosUsuario` (clase) — métodos relevantes ✅

**Descripción:**
- `login()`: obtiene cliente autenticado desde `ConexionBluesky`.
- `fetch_followers(...)`: manejo robusto de errores de API: distingue "Actor/Profile not found" (salta inmediatamente), detecta rate-limits (`429`/`RateLimit`) y aplica esperas, evita bucles infinitos y gestiona `KeyboardInterrupt`.
- `save_profiles(...)`: usa `SecureFileHandler` para leer/escribir `profiles_to_scan.json`; evita duplicados y escribe con permisos `0o600`.

**Justificación:**
- Asegura que datos descargados se persistan con permisos seguros, maneja condiciones de error y rate-limiting para evitar abusos; evita escribir datos en rutas inseguras.

---

## 5) `usuarios.BlueskyPostsFetcher` (clase) — métodos relevantes ✅

**Descripción:**
- Usa `SecureFileHandler` en `load_progress`, `load_profiles`, `save_progress` para acceso seguro a archivos JSON.
- Manejo de errores en `process_profiles` (skip para usuarios no encontrados, tratamiento de rate-limit, guardado periódico de progreso).
- Valida JSON al cargar (captura `JSONDecodeError`).

**Justificación:**
- Protección contra archivos corruptos o rutas maliciosas; persistencia segura del progreso y control de errores para evitar pérdida de datos o comportamiento inesperado.

---

## 6) `verificar_seguridad.py` (script y funciones) ✅

**Descripción:**
- `verificar_modelos()`: ejecuta `SecureModelHandler.verificar_todos()` y reporta integridad; sugiere acciones (reentrenar/recuperar) si hay inconsistencias.
- `verificar_permisos()`: verifica permisos de archivos sensibles listados (espera `0o600`) y muestra instrucciones de corrección.
- `listar_modelos()`, `main()`: utilidades para auditoría y resumen.

**Justificación:**
- Proporciona controles operativos y auditoría periódica para detectar modificaciones no autorizadas y configuraciones de permisos inseguras; guía la remediación.

---

## 7) Integración en scripts de predicción / entrenamiento ✅

**Descripción:**
- `prediccion/scripts/2_entrenar_modelo.py` y `3_predecir.py` usan `SecureModelHandler` para guardar/verificar modelos y abortan con recomendaciones si la verificación falla.

**Justificación:**
- Garantiza integridad en todo el flujo (guardar → verificar → usar); evita usar modelos comprometidos en producción.

---

## 8) Otras comprobaciones y prácticas observadas ✅

- Registro de checksums en `checksums.json`, con entrada en `.gitignore` para evitar exponer artefactos en control de versiones.
- Documentación en `README.md` y `EXPLICACION_NO_TECNICA_SCRIPTS.md` que describe las protecciones implementadas.

---

## Observaciones y Recomendaciones 💡

- Protección contra Pickle RCE: los checksums son una buena mitigación; sin embargo, se recomienda considerar formatos de serialización más seguros o añadir firmas digitales (GPG) a los artefactos para mayor robustez.
- `SecureModelHandler.cargar_modelo` realiza `pickle.load` tras verificar checksum — auditar quién puede escribir en `prediccion/modelos/` y, si es posible, restringir acceso para minimizar riesgo.
- `ConexionBluesky` utiliza variables de entorno: documentar el flujo de gestión de secretos (vaults, CI secrets) para evitar prácticas inseguras como poner credenciales en scripts o en la configuración.
- Recomendar ejecutar `verificar_seguridad.py` periódicamente (o como check en CI) para detectar regresiones de seguridad.

---

Si quieres que añada pruebas unitarias básicas para `SecureFileHandler` y `SecureModelHandler` o que integre `verificar_seguridad.py` en el pipeline de CI, indícalo y lo preparo.

# 📊 Análisis de Datos Bluesky

Módulo de análisis descriptivo de perfiles y publicaciones de Bluesky utilizando PySpark.

## 📋 Descripción

Este módulo realiza análisis estadístico completo de los datos extraídos, incluyendo:
- Análisis de perfiles de usuarios
- Análisis de comportamiento de publicaciones
- Métricas de engagement
- Patrones temporales
- Estadísticas de cuentas verificadas

---

## 🚀 Uso

### Ejecutar Análisis

```bash
cd analisis
python main_analisis.py
```

### Resultado

El análisis genera un reporte completo en formato Markdown:
- **Ubicación**: `analisis/resultados/analisis_descriptivo.md`
- **Contenido**: Todas las tablas, estadísticas y métricas del análisis

---

## ⚙️ Requisitos

### Java 17

PySpark requiere Java 17. Configúralo así (Windows PowerShell):

```powershell
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
java -version  # Debe mostrar version 17
```

### Configuración de Memoria

Si tienes problemas de memoria (`OutOfMemoryError`), edita `configuracion/config.yaml`:

```yaml
spark:
  driver_memory: "16g"      # Aumentar de 8g a 16g
  executor_memory: "16g"
```

---

## 📊 Métricas Analizadas

### Análisis de Perfiles

- **Estadísticas generales**: Total de usuarios, cuentas verificadas
- **Distribución de seguidores**: Min, max, promedio, mediana
- **Ratios de seguimiento**: Followers/Following
- **Cuenta por antigüedad**: Distribución temporal
- **Engagement**: Likes, replies, reposts
- **Top usuarios**: Por seguidores, por actividad

### Análisis de Posts

- **Volumen de publicaciones**: Total de posts, posts por usuario
- **Distribución de longitud**: Caracteres por post
- **Análisis de idiomas**: Distribución por idioma
- **Patrones temporales**: Posts por día de la semana, por hora
- **Engagement**: Likes, reposts, replies promedio
- **Tipos de contenido**: Posts con URLs, con menciones, con hashtags

---

## 🗂️ Estructura de Archivos

```
analisis/
├── main_analisis.py          # Script principal
├── analizar_profiles.py      # Análisis de perfiles
├── analizar_post.py          # Análisis de posts
├── carga_datos.py            # Carga de datos JSON
├── exportador_markdown.py    # Exportación a Markdown
├── spark_utils.py            # Utilidades de Spark
└── resultados/
    └── analisis_descriptivo.md  # Reporte generado
```

---

## 🔧 Configuración

Todos los parámetros se configuran en `configuracion/config.yaml`:

```yaml
analisis:
  top_n_resultados: 10      # Top N usuarios/posts a mostrar
  filas_mostrar: 15         # Filas en tablas
  truncar_tablas: 50        # Truncar texto largo

spark:
  app_name: "Bluesky Data Analysis"
  driver_memory: "8g"
  executor_memory: "8g"
  max_to_string_fields: 1000
  java_home: "C:\\Program Files\\Java\\jdk-17"
```

---

## 🛠️ Troubleshooting

### Error: java.lang.UnsupportedClassVersionError

**Causa**: Estás usando Java 8 en lugar de Java 17.

**Solución**: Configura Java 17 como se indica arriba.

### Error: OutOfMemoryError

**Causa**: No hay suficiente memoria para procesar los datos.

**Solución**: Aumenta `driver_memory` y `executor_memory` en `config.yaml`.

### Error: PATH_NOT_FOUND

**Causa**: Los archivos JSON no existen o están en otra ubicación.

**Solución**: Verifica que existan:
- `almacen/profiles_to_scan.json`
- `almacen/posts_usuarios.json`

---

## 📈 Ejemplo de Salida

El reporte incluye secciones como:

```markdown
# ANÁLISIS DE PERFILES

## Estadísticas Generales
- Total de usuarios: 14,900
- Usuarios verificados: 1,234 (8.3%)
- Usuarios sin verificar: 13,666 (91.7%)

## Distribución de Seguidores
+-------+----------+
|  stat |    value |
+-------+----------+
|   min |        0 |
|   max |  1234567 |
|  mean |   456.78 |
|median |      123 |
+-------+----------+

...
```

---

## 🔄 Actualizar Análisis

Si añades más datos con el scraper, simplemente vuelve a ejecutar:

```bash
python main_analisis.py
```

El script sobrescribirá `analisis_descriptivo.md` con los nuevos resultados.

---

## 📚 Documentación Relacionada

- **Configuración**: [`../configuracion/README.md`](../configuracion/README.md)
- **Extracción de datos**: [`../README.md`](../README.md)

---

¿Preguntas? Revisa el código fuente en los archivos `.py` de esta carpeta.

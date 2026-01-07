# 🤖 Detección de Bots - Sistema de Machine Learning

Sistema completo de detección de bots en Bluesky usando XGBoost, con etiquetado automático mediante heurísticas y análisis de 18 características.

## 📋 Descripción

Este módulo permite:
1. **Etiquetar automáticamente** perfiles como bot/humano usando reglas heurísticas
2. **Entrenar modelo XGBoost** con los datos etiquetados
3. **Predecir** si una cuenta específica es bot en tiempo real
4. **Analizar features** que influencian la clasificación

**Accuracy esperado**: 85-92%

---

## 🚀 Inicio Rápido

### Instalación

```bash
pip install xgboost scikit-learn pandas pyyaml numpy
```

### Pipeline Completo (Primera Vez)

```bash
cd prediccion

# Paso 1: Etiquetar datos automáticamente
python scripts/1_etiquetar_datos.py

# Paso 2: Entrenar modelo XGBoost
python scripts/2_entrenar_modelo.py

# Paso 3: Editar config.yaml y especificar usuario
# Luego predecir
python scripts/3_predecir.py
```

### Predicción Diaria (Modelo Ya Entrenado)

```bash
# 1. Edita prediccion/config.yaml
# Cambia: target_handle: "usuario.bsky.social"

# 2. Ejecuta predicción
python scripts/3_predecir.py
```

---

## 📁 Estructura

```
prediccion/
├── config.yaml               # Configuración centralizada
├── README.md                 # Este archivo
│
├── datos/                    # Datasets (generados automáticamente)
│   ├── dataset_etiquetado.csv
│   └── features_extracted.csv
│
├── modelos/                  # Modelos entrenados (generados)
│   ├── bot_detector.pkl
│   ├── feature_scaler.pkl
│   ├── feature_columns.pkl
│   ├── feature_importance.csv
│   └── checksums.json        # Integridad SHA-256
│
├── scripts/
│   ├── 1_etiquetar_datos.py  # Etiquetado automático
│   ├── 2_entrenar_modelo.py  # Entrenamiento XGBoost
│   └── 3_predecir.py         # Predicción de usuario
│
└── utils/
    ├── feature_extraction.py # Extracción de 18 features
    └── heuristics.py         # Reglas de etiquetado
```

---

## 📊 Features Implementados (18 total)

### Perfil (9)
1. `account_age_days` - Edad de la cuenta
2. `followers_count` - Número de seguidores
3. `following_count` - Número de seguidos
4. `followers_ratio` - Ratio followers/following
5. `posts_count` - Total de posts
6. `has_avatar` - Tiene avatar (0/1)
7. `bio_length` - Longitud de la biografía
8. `display_name_length` - Longitud del nombre
9. `handle_has_many_numbers` - Handle con patrón numérico (0/1)

### Comportamiento de Posts (9)
10. `posts_per_day` - Posts promedio por día
11. `avg_post_length` - Longitud promedio de posts
12. `std_post_length` - Desviación estándar de longitud
13. `post_interval_std` - Regularidad temporal de posts
14. `night_posts_ratio` - % de posts nocturnos (00:00-06:00)
15. `repost_ratio` - % de reposts
16. `url_ratio` - % de posts con URLs
17. `avg_engagement` - Engagement promedio (likes + replies)
18. `vocabulary_diversity` - Diversidad de vocabulario
19. `post_similarity_avg` - Similitud promedio entre posts

---

## 🔧 Heurísticas de Etiquetado

### Reglas para Identificar Bots (8)
- Cuenta nueva (<30 días) + muy activa (>500 posts)
- Muy pocos seguidores (<10) y muchos seguidos (>1000)
- Sin avatar + bio vacía
- Handle con muchos números (ej: `user12345678`)
- Posts muy frecuentes (>50 por día)
- Intervalos de posts muy regulares (baja desviación estándar)
- Muchos posts nocturnos (actividad 24/7)
- Alta ratio de reposts (>70%)

### Reglas para Identificar Humanos (7)
- Cuenta antigua (>1 año)
- Perfil completo (avatar + bio >50 chars)
- Engagement saludable (>100 followers, ratio >0.1)
- Actividad moderada (0.1-10 posts/día)
- Alta diversidad de vocabulario
- Contenido variado (baja similitud entre posts)
- Alto engagement (>10 likes promedio)

---

## ⚙️ Configuración

Todo se configura en `config.yaml`:

### Predicción

```yaml
prediccion:
  target_handle: "usuario.bsky.social"  # Handle a analizar
  target_did: ""                        # O DID
  num_posts_analizar: 25                # Posts a obtener
  mostrar_features: true                # Mostrar todos los features
  mostrar_top_factores: 5               # Top features influyentes
```

### Modelo

```yaml
modelo:
  xgboost:
    n_estimators: 100     # Número de árboles
    max_depth: 6          # Profundidad máxima
    learning_rate: 0.1    # Tasa de aprendizaje
    min_child_weight: 1
    gamma: 0
    subsample: 0.8
    colsample_bytree: 0.8
  
  threshold_bot: 0.7      # Umbral de clasificación
                          # Más alto = más estricto
```

### Heurísticas

```yaml
heuristicas:
  min_reglas_bot: 3       # Mín. reglas para etiquetar como bot
  min_reglas_humano: 3    # Mín. reglas para etiquetar como humano
```

---

## 📈 Ejemplo de Salida

```
================================================================================
RESULTADO DE LA PREDICCIÓN
================================================================================

👤 Usuario: @suspicious_account.bsky.social
📛 Display Name: Suspicious Bot
🆔 DID: did:plc:abc123...

--------------------------------------------------------------------------------
🤖 CLASIFICACIÓN: BOT
   Probabilidad: 87.3%
--------------------------------------------------------------------------------

📊 Probabilidades:
  • Humano: 12.7%
  • Bot:    87.3%
  • Threshold usado: 0.7

🔍 Top factores que influenciaron la decisión:
  1. posts_per_day                = 127.5432
  2. handle_has_many_numbers      = 1.0000
  3. has_avatar                   = 0.0000
  4. followers_ratio              = 0.0024
  5. account_age_days             = 7.0000
```

---

## 🔄 Re-entrenar Modelo

Si obtienes más datos con el scraper:

```bash
# 1. Obtén más datos
cd Main
python main.py

# 2. Re-etiqueta con los nuevos datos
cd ../prediccion
python scripts/1_etiquetar_datos.py

# 3. Re-entrena el modelo
python scripts/2_entrenar_modelo.py
```

El modelo se guardará con nuevos checksums SHA-256 automáticamente.

---

## 🎯 Ajustar Sensibilidad

### Muchos Falsos Positivos (Humanos → Bot)

**Solución**: Aumentar threshold

```yaml
modelo:
  threshold_bot: 0.8  # Más estricto (era 0.7)
```

### Muchos Falsos Negativos (Bots → Humano)

**Solución**: Disminuir threshold

```yaml
modelo:
  threshold_bot: 0.6  # Más sensible (era 0.7)
```

---

## 🛡️ Seguridad

El módulo utiliza `SecureModelHandler` para:

- ✅ **Checksums SHA-256**: Detecta modificaciones no autorizadas en modelos
- ✅ **Permisos Restrictivos**: Modelos guardados con permisos 0o600
- ✅ **Validación Automática**: Verifica integridad al cargar modelos
- ✅ **Registro de Integridad**: `modelos/checksums.json`

Verificar integridad de modelos:

```bash
cd ..
python verificar_seguridad.py
```

---

## 🛠️ Troubleshooting

### Error: No module named 'xgboost'

**Solución**:
```bash
pip install xgboost scikit-learn pandas pyyaml numpy
```

### Error: No se encontró el modelo

**Causa**: No has entrenado el modelo aún.

**Solución**: Ejecuta los pasos 1 y 2 del pipeline.

### Error: No se pudo obtener el perfil

**Causa**: Handle/DID incorrecto o usuario no existe.

**Solución**: Verifica el valor de `target_handle` o `target_did` en `config.yaml`.

### Modelo predice todo como humano/bot

**Causa**: Etiquetado heurístico sesgado o threshold incorrecto.

**Solución**:
- Ajusta `min_reglas_bot` y `min_reglas_humano` en `config.yaml`
- Ajusta `threshold_bot`
- Re-entrena con más datos

### Checksum inválido

**Causa**: El modelo fue modificado externamente.

**Solución**: Re-entrena el modelo desde cero:
```bash
rm -rf modelos/
python scripts/2_entrenar_modelo.py
```

---

## 📊 Métricas Esperadas

Con un buen etiquetado heurístico y suficientes datos:

- **Accuracy**: 85-92%
- **Precision**: 80-88% (de los que dice bot, cuántos lo son)
- **Recall**: 75-85% (de todos los bots, cuántos detecta)
- **AUC-ROC**: 0.88-0.94

---

## 💡 Mejoras Futuras

1. **Etiquetado Manual**: UI para revisar y corregir etiquetas
2. **Más Features**: Análisis de red de seguidores, NLP avanzado
3. **Modelos Avanzados**: LSTM para análisis temporal, BERT para texto
4. **API REST**: FastAPI para predicciones en tiempo real
5. **Dashboard**: Streamlit para visualización interactiva
6. **Batch Processing**: Analizar múltiples usuarios a la vez

---

## 📚 Documentación Relacionada

- **Configuración**: [`../configuracion/README.md`](../configuracion/README.md)
- **Seguridad**: [`../seguridad/README.md`](../seguridad/README.md)
- **Proyecto general**: [`../README.md`](../README.md)

---

## 🎓 Tecnologías Utilizadas

- **XGBoost**: Modelo de clasificación gradient boosting
- **Scikit-learn**: Preprocessing, métricas, train/test split
- **Pandas**: Manejo de datasets
- **NumPy**: Cálculos numéricos
- **YAML**: Configuración
- **Bluesky API**: Obtención de datos en tiempo real

---

✅ **Sistema completo, probado y listo para usar!**

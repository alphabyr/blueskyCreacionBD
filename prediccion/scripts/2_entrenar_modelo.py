"""
PASO 2: Entrenar modelo XGBoost
Lee dataset etiquetado y entrena el modelo de detección de bots
"""
import os
import sys
import yaml
import pandas as pd
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import xgboost as xgb

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from seguridad.secure_model_handler import SecureModelHandler

def cargar_config():
    """Carga la configuración desde config.yaml"""
    config_path = Path(__file__).parent.parent / 'config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def cargar_dataset(config):
    """Carga el dataset etiquetado"""
    base_dir = Path(__file__).parent.parent
    dataset_path = base_dir / config['rutas']['dataset_etiquetado']
    
    print(f"📖 Cargando dataset desde: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"✓ Dataset cargado: {len(df)} muestras")
    
    return df

def preparar_datos(df, config):
    """Prepara los datos para el entrenamiento"""
    print("\n🔧 Preparando datos...")
    
    # Columnas a excluir (metadata, no features)
    exclude_cols = ['did', 'handle', 'label']
    
    # Features = todas las columnas excepto las excluidas
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols]
    y = df['label']
    
    print(f"  • Features: {len(feature_cols)}")
    print(f"  • Muestras: {len(df)}")
    print(f"  • Distribución labels:")
    print(f"    - Humanos (0): {(y == 0).sum()}")
    print(f"    - Bots (1): {(y == 1).sum()}")
    
    # Dividir en entrenamiento/prueba
    test_size = config['modelo']['train_test_split']['test_size']
    random_state = config['modelo']['train_test_split']['random_state']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y  # Mantener proporción de clases
    )
    
    print(f"\n✓ División completada:")
    print(f"  • Entrenamiento: {len(X_train)} muestras")
    print(f"  • Prueba: {len(X_test)} muestras")
    
    # Escalar características
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_cols

def entrenar_modelo(X_train, y_train, config):
    """Entrena el modelo XGBoost"""
    print("\n🤖 Entrenando modelo XGBoost...")
    
    # Parámetros desde config
    params = config['modelo']['xgboost']
    
    model = xgb.XGBClassifier(**params)
    
    # Entrenar
    model.fit(
        X_train, y_train,
        eval_set=[(X_train, y_train)],
        verbose=False
    )
    
    print("✓ Modelo entrenado exitosamente")
    
    return model

def evaluar_modelo(model, X_test, y_test, feature_cols):
    """Evalúa el modelo en el test set"""
    print("\n📊 Evaluando modelo...")
    
    # Predicciones
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Métricas
    print("\n" + "=" * 60)
    print("REPORTE DE CLASIFICACIÓN")
    print("=" * 60)
    print(classification_report(y_test, y_pred, target_names=['Humano', 'Bot']))
    
    print("\n" + "=" * 60)
    print("MATRIZ DE CONFUSIÓN")
    print("=" * 60)
    cm = confusion_matrix(y_test, y_pred)
    print(f"          Predicho")
    print(f"           H    B")
    print(f"Real H  {cm[0][0]:4d} {cm[0][1]:4d}")
    print(f"     B  {cm[1][0]:4d} {cm[1][1]:4d}")
    
    # AUC-ROC
    auc = roc_auc_score(y_test, y_pred_proba)
    print(f"\n🎯 AUC-ROC: {auc:.4f}")
    
    # Feature importance
    print("\n" + "=" * 60)
    print("TOP 10 FEATURES MÁS IMPORTANTES")
    print("=" * 60)
    
    importance = model.feature_importances_
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(10).iterrows():
        print(f"{row['feature']:30s} {row['importance']:.4f}")
    
    return feature_importance

def guardar_modelo(model, scaler, feature_cols, feature_importance, config):
    """Guarda el modelo y componentes necesarios de forma segura"""
    print("\n💾 Guardando modelo...")
    
    base_dir = Path(__file__).parent.parent
    modelos_dir = base_dir / 'modelos'
    
    # Crear handler seguro para modelos
    model_handler = SecureModelHandler(modelos_dir)
    
    # Guardar modelo con verificación de integridad
    modelo_path = model_handler.guardar_modelo(model, 'bot_detector.pkl', permisos=0o600)
    print(f"  ✓ Modelo: {modelo_path}")
    
    # Guardar scaler
    scaler_path = model_handler.guardar_modelo(scaler, 'feature_scaler.pkl', permisos=0o600)
    print(f"  ✓ Scaler: {scaler_path}")
    
    # Guardar columnas de features
    cols_path = model_handler.guardar_modelo(feature_cols, 'feature_columns.pkl', permisos=0o600)
    print(f"  ✓ Feature columns: {cols_path}")
    
    # Guardar feature importance (CSV no necesita pickle)
    importance_path = modelos_dir / 'feature_importance.csv'
    feature_importance.to_csv(importance_path, index=False)
    print(f"  ✓ Feature importance: {importance_path}")
    
    print("\n🔒 Checksums de integridad generados y guardados.")

def main():
    print("=" * 80)
    print("PASO 2: ENTRENAMIENTO DEL MODELO")
    print("=" * 80)
    
    # Cargar configuración
    config = cargar_config()
    
    # Cargar dataset
    df = cargar_dataset(config)
    
    # Preparar datos
    X_train, X_test, y_train, y_test, scaler, feature_cols = preparar_datos(df, config)
    
    # Entrenar modelo
    model = entrenar_modelo(X_train, y_train, config)
    
    # Evaluar modelo
    feature_importance = evaluar_modelo(model, X_test, y_test, feature_cols)
    
    # Guardar modelo
    guardar_modelo(model, scaler, feature_cols, feature_importance, config)
    
    print("\n" + "=" * 80)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("=" * 80)
    print("\n➡️  Siguiente paso: python scripts/3_predecir.py")

if __name__ == "__main__":
    main()

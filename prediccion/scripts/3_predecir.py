"""
PASO 3: Predecir si un usuario es bot
Lee un handle/DID desde config.yaml y predice usando el modelo entrenado
"""
import os
import sys
import yaml
import pickle
import pandas as pd
from pathlib import Path

# Añadir directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from prediccion.utils.feature_extraction import FeatureExtractor
from gestor.conexion import ConexionBluesky
from seguridad.secure_model_handler import SecureModelHandler

def cargar_config():
    """Carga la configuración desde config.yaml"""
    config_path = Path(__file__).parent.parent / 'config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def cargar_modelo(config):
    """Carga el modelo entrenado y componentes de forma segura"""
    base_dir = Path(__file__).parent.parent
    modelos_dir = base_dir / 'modelos'
    
    print("📦 Cargando modelo entrenado...")
    
    # Crear handler seguro para modelos
    model_handler = SecureModelHandler(modelos_dir)
    
    try:
        # Cargar modelo con verificación de integridad
        print("  • Verificando integridad de archivos...")
        model = model_handler.cargar_modelo('bot_detector.pkl', verificar_integridad=True)
        print("    ✓ Modelo cargado y verificado")
        
        scaler = model_handler.cargar_modelo('feature_scaler.pkl', verificar_integridad=True)
        print("    ✓ Scaler cargado y verificado")
        
        feature_cols = model_handler.cargar_modelo('feature_columns.pkl', verificar_integridad=True)
        print("    ✓ Feature columns cargado y verificado")
        
        print("✓ Todos los componentes cargados exitosamente")
        
    except ValueError as e:
        print(f"\n⚠️  ERROR DE SEGURIDAD: {e}")
        print("\n🔴 ACCIÓN REQUERIDA:")
        print("  1. Verifica que los archivos no hayan sido modificados manualmente")
        print("  2. Si modificaste los modelos, vuelve a entrenar: python scripts/2_entrenar_modelo.py")
        print("  3. Si sospechas un ataque, elimina la carpeta 'modelos/' y reentrena desde cero")
        raise
    
    return model, scaler, feature_cols

def obtener_datos_usuario(handle=None, did=None, config=None):
    """Obtiene datos de un usuario desde la API de Bluesky"""
    print(f"\n🔍 Buscando usuario...")
    
    # Conectar a Bluesky
    conexion = ConexionBluesky()
    client = conexion.get_client()
    
    # Obtener perfil
    identifier = did if did else handle
    print(f"  • Identificador: {identifier}")
    
    try:
        profile_response = client.get_profile(actor=identifier)
        profile = profile_response.model_dump(mode='json')
        print(f"  ✓ Perfil obtenido: @{profile.get('handle')}")
    except Exception as e:
        print(f"  ✗ Error obteniendo perfil: {e}")
        return None, None
    
    # Obtener posts
    num_posts = config['prediccion']['num_posts_analizar']
    try:
        posts_response = client.get_author_feed(
            actor=identifier,
            limit=num_posts
        )
        
        posts = []
        for feed_item in posts_response.feed:
            post = feed_item.post
            posts.append({
                'text': post.record.text,
                'createdAt': post.record.created_at,
                'likeCount': post.like_count,
                'replyCount': post.reply_count,
                'repostCount': post.repost_count
            })
        
        print(f"  ✓ Posts obtenidos: {len(posts)}")
    except Exception as e:
        print(f"  ⚠️  Error obteniendo posts: {e}")
        posts = []
    
    return profile, posts

def extraer_features(profile, posts):
    """Extrae características del perfil y posts"""
    print("\n🔬 Extrayendo características...")
    
    extractor = FeatureExtractor()
    features = extractor.extract_profile_features(profile, posts)
    
    print(f"  ✓ {len(features)} features extraídos")
    
    return features

def predecir(features, model, scaler, feature_cols, config):
    """Predice si el usuario es bot"""
    print("\n🤖 Ejecutando predicción...")
    
    # Preparar features en el orden correcto
    X = pd.DataFrame([features])[feature_cols]
    
    # Escalar
    X_scaled = scaler.transform(X)
    
    # Predecir
    prob = model.predict_proba(X_scaled)[0]
    prob_humano = prob[0]
    prob_bot = prob[1]
    
    # Clasificación basada en threshold
    threshold = config['modelo']['threshold_bot']
    es_bot = prob_bot > threshold
    
    return {
        'prob_humano': prob_humano,
        'prob_bot': prob_bot,
        'es_bot': es_bot,
        'threshold': threshold
    }

def mostrar_resultado(profile, resultado, features, model, feature_cols, config):
    """Muestra el resultado de la predicción"""
    print("\n" + "=" * 80)
    print("RESULTADO DE LA PREDICCIÓN")
    print("=" * 80)
    
    # Información del usuario
    print(f"\n👤 Usuario: @{profile.get('handle')}")
    print(f"📛 Display Name: {profile.get('display_name', 'N/A')}")
    print(f"🆔 DID: {profile.get('did')}")
    
    # Predicción
    print("\n" + "-" * 80)
    if resultado['es_bot']:
        print(f"🤖 CLASIFICACIÓN: BOT")
        print(f"   Probabilidad: {resultado['prob_bot']:.1%}")
    else:
        print(f"👤 CLASIFICACIÓN: HUMANO")
        print(f"   Probabilidad: {resultado['prob_humano']:.1%}")
    print("-" * 80)
    
    # Detalles
    print(f"\n📊 Probabilidades:")
    print(f"  • Humano: {resultado['prob_humano']:.1%}")
    print(f"  • Bot:    {resultado['prob_bot']:.1%}")
    print(f"  • Threshold usado: {resultado['threshold']}")
    
    # Top factores si está configurado
    if config['prediccion']['mostrar_top_factores'] > 0:
        print("\n🔍 Top factores que influenciaron la decisión:")
        
        # Obtener feature importance del modelo
        importance = model.feature_importances_
        feature_values = pd.DataFrame([features])[feature_cols].iloc[0].values
        
        # Calcular contribución (importance * valor normalizado)
        contributions = []
        for i, (feat, imp, val) in enumerate(zip(feature_cols, importance, feature_values)):
            contributions.append({
                'feature': feat,
                'importance': imp,
                'value': val,
                'contribution': abs(imp * val)
            })
        
        # Ordenar por contribución
        contributions.sort(key=lambda x: x['contribution'], reverse=True)
        
        # Mostrar top N
        top_n = config['prediccion']['mostrar_top_factores']
        for i, c in enumerate(contributions[:top_n], 1):
            print(f"  {i}. {c['feature']:30s} = {c['value']:.4f}")
    
    # Mostrar features si está configurado
    if config['prediccion']['mostrar_features']:
        print("\n📋 Features extraídos:")
        for feat in feature_cols:
            if feat in features:
                print(f"  • {feat:30s} = {features[feat]:.4f}")

def main():
    print("=" * 80)
    print("DETECTOR DE BOTS - PREDICCIÓN")
    print("=" * 80)
    
    # Cargar configuración
    config = cargar_config()
    
    # Obtener handle/DID desde config
    handle = config['prediccion'].get('target_handle', '').strip()
    did = config['prediccion'].get('target_did', '').strip()
    
    if not handle and not did:
        print("\n❌ ERROR: Debes especificar 'target_handle' o 'target_did' en config.yaml")
        print("\nEjemplo en prediccion/config.yaml:")
        print("  prediccion:")
        print("    target_handle: \"elonmusk.bsky.social\"  # o")
        print("    target_did: \"did:plc:abc123...\"")
        return
    
    # Cargar modelo
    model, scaler, feature_cols = cargar_modelo(config)
    
    # Obtener datos del usuario
    profile, posts = obtener_datos_usuario(handle=handle, did=did, config=config)
    
    if not profile:
        print("\n❌ No se pudo obtener el perfil del usuario")
        return
    
    # Extraer features
    features = extraer_features(profile, posts)
    
    # Predecir
    resultado = predecir(features, model, scaler, feature_cols, config)
    
    # Mostrar resultado
    mostrar_resultado(profile, resultado, features, model, feature_cols, config)
    
    print("\n" + "=" * 80)
    print("✅ PREDICCIÓN COMPLETADA")
    print("=" * 80)

if __name__ == "__main__":
    main()

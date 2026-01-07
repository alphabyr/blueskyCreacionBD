"""
Generador de Visualizaciones Bluesky - Versión Simplificada
============================================================
Genera 25 gráficos garantizados con los datos disponibles.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 10

# Config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configuracion.load_config import config


def cargar_datos():
    """Carga perfiles y posts"""
    print("📥 Cargando datos...")
    
    # Rutas relativas al directorio del script (analisis/)
    base_dir = Path(__file__).parent.parent  # Ir a bluesky2/
    
    # Perfiles
    profiles = pd.DataFrame(json.load(open(base_dir / config.get_ruta_profiles(), 'r', encoding='utf-8')))
    profiles['created_date'] = pd.to_datetime(profiles['created_at'], errors='coerce', utc=True).dt.tz_localize(None)
    profiles['account_age_days'] = (pd.Timestamp.now() - profiles['created_date']).dt.days
    profiles['bio_length'] = profiles['description'].fillna('').str.len()
    profiles['name_length'] = profiles['display_name'].fillna('').str.len()
    profiles['handle_length'] = profiles['handle'].str.len()
    
    # Posts
    posts_data = json.load(open(base_dir / config.get_ruta_posts_json(), 'r', encoding='utf-8'))
    all_posts = []
    for did, data in posts_data.items():
        if 'posts' in data:
            for post in data['posts']:
                post['author_did'] = did
                all_posts.append(post)
    
    posts = pd.DataFrame(all_posts)
    posts['created_date'] = pd.to_datetime(posts['createdAt'], errors='coerce', utc=True).dt.tz_localize(None)
    posts['hour'] = posts['created_date'].dt.hour
    posts['day_of_week'] = posts['created_date'].dt.day_name()
    posts['month'] = posts['created_date'].dt.month
    posts['text_length'] = posts['text'].fillna('').str.len()
    posts['total_engagement'] = posts['likeCount'] + posts['replyCount'] + posts['repostCount']
    
    print(f"✓ {len(profiles)} perfiles, {len(posts)} posts")
    return profiles, posts


def main():
    OUTPUT_DIR = Path(__file__).parent / "resultados" / "graficos"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("  GENERADOR DE GRÁFICOS - BLUESKY")
    print("=" * 60)
    
    profiles, posts = cargar_datos()
    count = 0
    
    print("\n🎨 Generando gráficos...\n")
    
    # ===== GRÁFICOS DE PERFILES (10) =====
    
    # 1. Distribución de longitud de handles
    plt.figure(figsize=(12, 6))
    sns.histplot(profiles['handle_length'], bins=30, kde=True, color='skyblue')
    plt.title('Distribución de Longitud de Handles', fontsize=14, fontweight='bold')
    plt.xlabel('Longitud'); plt.ylabel('Frecuencia')
    plt.savefig(OUTPUT_DIR / '01_longitud_handles.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Longitud de handles")
    
    # 2. Usuarios con/sin avatar
    has_avatar = profiles['avatar'].notna().value_counts()
    plt.figure(figsize=(10, 7))
    plt.pie(has_avatar.values, labels=['Con Avatar', 'Sin Avatar'], autopct='%1.1f%%',
            startangle=90, colors=['#66c2a5', '#fc8d62'])
    plt.title('Usuarios con/sin Avatar', fontsize=14, fontweight='bold')
    plt.savefig(OUTPUT_DIR / '02_usuarios_avatar.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Usuarios con avatar")
    
    # 3. Longitud de biografías
    plt.figure(figsize=(12, 6))
    sns.histplot(profiles['bio_length'], bins=50, kde=True, color='teal')
    plt.title('Distribución de Longitud de Biografías', fontsize=14, fontweight='bold')
    plt.xlabel('Longitud (caracteres)'); plt.ylabel('Frecuencia')
    plt.savefig(OUTPUT_DIR / '03_longitud_bio.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Longitud de biografías")
    
    # 4. Longitud de nombres
    plt.figure(figsize=(12, 6))
    sns.histplot(profiles['name_length'], bins=30, kde=True, color='coral')
    plt.title('Distribución de Longitud de Nombres', fontsize=14, fontweight='bold')
    plt.xlabel('Longitud (caracteres)'); plt.ylabel('Frecuencia')
    plt.savefig(OUTPUT_DIR / '04_longitud_nombres.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Longitud de nombres")
    
    # 5. Evolución de creación de cuentas
    monthly = profiles.set_index('created_date').resample('M').size()
    plt.figure(figsize=(14, 6))
    monthly.plot(kind='line', marker='o', color='navy', linewidth=2)
    plt.title('Evolución de Creación de Cuentas', fontsize=14, fontweight='bold')
    plt.xlabel('Fecha'); plt.ylabel('Nuevas Cuentas')
    plt.grid(True, alpha=0.3)
    plt.savefig(OUTPUT_DIR / '05_evolucion_cuentas.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Evolución de cuentas")
    
    # 6. Antigüedad de cuentas
    plt.figure(figsize=(12, 6))
    sns.histplot(profiles['account_age_days'], bins=50, kde=True, color='brown')
    plt.title('Distribución de Antigüedad de Cuentas', fontsize=14, fontweight='bold')
    plt.xlabel('Antigüedad (días)'); plt.ylabel('Frecuencia')
    plt.savefig(OUTPUT_DIR / '06_antiguedad_cuentas.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Antigüedad de cuentas")
    
    # 7. Cuentas por año
    yearly = profiles.set_index('created_date').resample('Y').size()
    plt.figure(figsize=(12, 6))
    years = [d.year for d in yearly.index]
    plt.bar(years, yearly.values, color='steelblue', width=0.6)
    plt.title('Cuentas Creadas por Año', fontsize=14, fontweight='bold')
    plt.xlabel('Año'); plt.ylabel('Cuentas')
    plt.xticks(years)
    plt.grid(axis='y', alpha=0.3)
    plt.savefig(OUTPUT_DIR / '07_cuentas_por_año.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Cuentas por año")
    
    # 8. Categorías de origen
    cat_counts = profiles['origen_categoria'].value_counts()
    plt.figure(figsize=(12, 7))
    plt.pie(cat_counts.values, labels=cat_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('Distribución por Categoría de Origen', fontsize=14, fontweight='bold')
    plt.savefig(OUTPUT_DIR / '08_categorias_origen.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Categorías de origen")
    
    # 9. Top semillas
    semillas = profiles['origen_semilla'].value_counts().head(15)
    plt.figure(figsize=(12, 8))
    sns.barplot(x=semillas.values, y=semillas.index, palette='viridis')
    plt.title('Top 15 Semillas por Seguidores Recopilados', fontsize=14, fontweight='bold')
    plt.xlabel('Seguidores'); plt.ylabel('Semilla')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '09_top_semillas.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Top semillas")
    
    # 10. Top handles más largos
    top_long = profiles.nlargest(20, 'handle_length')[['handle', 'handle_length']]
    plt.figure(figsize=(12, 10))
    sns.barplot(data=top_long, y='handle', x='handle_length', palette='plasma')
    plt.title('Top 20 Handles Más Largos', fontsize=14, fontweight='bold')
    plt.xlabel('Longitud'); plt.ylabel('Handle')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '10_handles_largos.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Handles más largos")
    
    # ===== GRÁFICOS DE POSTS (10) =====
    
    # 11. Longitud de posts
    plt.figure(figsize=(12, 6))
    sns.histplot(posts['text_length'], bins=50, kde=True, color='coral')
    plt.title('Distribución de Longitud de Posts', fontsize=14, fontweight='bold')
    plt.xlabel('Longitud (caracteres)'); plt.ylabel('Frecuencia')
    plt.savefig(OUTPUT_DIR / '11_longitud_posts.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Longitud de posts")
    
    # 12. Posts por hora
    hour_counts = posts['hour'].value_counts().sort_index()
    plt.figure(figsize=(14, 6))
    plt.bar(hour_counts.index, hour_counts.values, color='skyblue', width=0.8)
    plt.title('Distribución de Posts por Hora', fontsize=14, fontweight='bold')
    plt.xlabel('Hora'); plt.ylabel('Posts')
    plt.xticks(range(24))
    plt.grid(axis='y', alpha=0.3)
    plt.savefig(OUTPUT_DIR / '12_posts_por_hora.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Posts por hora")
    
    # 13. Posts por día de semana
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = posts['day_of_week'].value_counts().reindex(days_order, fill_value=0)
    plt.figure(figsize=(12, 6))
    plt.bar(range(7), day_counts.values, color='lightgreen', width=0.7)
    plt.title('Posts por Día de la Semana', fontsize=14, fontweight='bold')
    plt.xlabel('Día'); plt.ylabel('Posts')
    plt.xticks(range(7), ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'])
    plt.grid(axis='y', alpha=0.3)
    plt.savefig(OUTPUT_DIR / '13_posts_por_dia.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Posts por día")
    
    # 14. Evolución temporal
    daily = posts.set_index('created_date').resample('D').size()
    plt.figure(figsize=(14, 6))
    daily.plot(kind='line', color='navy')
    plt.title('Evolución de Posts en el Tiempo', fontsize=14, fontweight='bold')
    plt.xlabel('Fecha'); plt.ylabel('Posts')
    plt.grid(True, alpha=0.3)
    plt.savefig(OUTPUT_DIR / '14_evolucion_posts.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Evolución de posts")
    
    # 15. Heatmap hora x día
    pivot = posts.pivot_table(index='day_of_week', columns='hour', 
                              values='text', aggfunc='count', fill_value=0).reindex(days_order)
    plt.figure(figsize=(16, 7))
    sns.heatmap(pivot, cmap='YlOrRd', annot=False, linewidths=0.5)
    plt.title('Heatmap: Posts por Hora y Día', fontsize=14, fontweight='bold')
    plt.xlabel('Hora'); plt.ylabel('Día')
    plt.yticks(range(7), ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'], rotation=0)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '15_heatmap_hora_dia.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Heatmap hora-día")
    
    # 16. Distribución de likes
    plt.figure(figsize=(12, 6))
    sns.histplot(posts['likeCount'], bins=50, kde=True, color='red')
    plt.title('Distribución de Likes', fontsize=14, fontweight='bold')
    plt.xlabel('Likes'); plt.ylabel('Frecuencia')
    plt.yscale('log')
    plt.savefig(OUTPUT_DIR / '16_distribucion_likes.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Distribución de likes")
    
    # 17. Distribución de reposts
    plt.figure(figsize=(12, 6))
    sns.histplot(posts['repostCount'], bins=50, kde=True, color='blue')
    plt.title('Distribución de Reposts', fontsize=14, fontweight='bold')
    plt.xlabel('Reposts'); plt.ylabel('Frecuencia')
    plt.yscale('log')
    plt.savefig(OUTPUT_DIR / '17_distribucion_reposts.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Distribución de reposts")
    
    # 18. Distribución de replies
    plt.figure(figsize=(12, 6))
    sns.histplot(posts['replyCount'], bins=50, kde=True, color='purple')
    plt.title('Distribución de Replies', fontsize=14, fontweight='bold')
    plt.xlabel('Replies'); plt.ylabel('Frecuencia')
    plt.yscale('log')
    plt.savefig(OUTPUT_DIR / '18_distribucion_replies.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Distribución de replies")
    
    # 19. Posts por mes
    month_counts = posts['month'].value_counts().sort_index()
    month_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                   'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    plt.figure(figsize=(12, 6))
    plt.bar(month_counts.index, month_counts.values, color='mediumseagreen')
    plt.title('Posts por Mes', fontsize=14, fontweight='bold')
    plt.xlabel('Mes'); plt.ylabel('Posts')
    plt.xticks(range(1, 13), month_names)
    plt.grid(axis='y', alpha=0.3)
    plt.savefig(OUTPUT_DIR / '19_posts_por_mes.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Posts por mes")
    
    # 20. Engagement total
    plt.figure(figsize=(12, 6))
    sns.histplot(posts['total_engagement'], bins=50, kde=True, color='orange')
    plt.title('Distribución de Engagement Total', fontsize=14, fontweight='bold')
    plt.xlabel('Engagement (Likes + Replies + Reposts)'); plt.ylabel('Frecuencia')
    plt.yscale('log')
    plt.savefig(OUTPUT_DIR / '20_engagement_total.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Engagement total")
    
    # ===== GRÁFICOS CRUZADOS (5) =====
    
    # 21. Posts por usuario
    posts_per_user = posts['author_did'].value_counts()
    plt.figure(figsize=(12, 6))
    sns.histplot(posts_per_user.values, bins=25, kde=True, color='indigo')
    plt.title('Distribución de Posts por Usuario', fontsize=14, fontweight='bold')
    plt.xlabel('Posts por Usuario'); plt.ylabel('Frecuencia')
    plt.savefig(OUTPUT_DIR / '21_posts_por_usuario.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Posts por usuario")
    
    # 22. Top usuarios activos
    top_users = posts_per_user.head(20)
    user_handles = []
    for did, pcount in top_users.items():
        prof = profiles[profiles['did'] == did]
        handle = prof['handle'].iloc[0] if not prof.empty else did[:20]
        user_handles.append({'handle': handle, 'posts': pcount})
    
    user_df = pd.DataFrame(user_handles)
    plt.figure(figsize=(12, 10))
    sns.barplot(data=user_df, y='handle', x='posts', palette='plasma')
    plt.title('Top 20 Usuarios Más Activos', fontsize=14, fontweight='bold')
    plt.xlabel('Posts'); plt.ylabel('Usuario')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '22_usuarios_activos.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Usuarios más activos")
    
    # 23. Comparación métricas engagement
    totals = [posts['likeCount'].sum(), posts['repostCount'].sum(), posts['replyCount'].sum()]
    plt.figure(figsize=(10, 7))
    plt.pie(totals, labels=['Likes', 'Reposts', 'Replies'], autopct='%1.1f%%',
            startangle=90, colors=['#e74c3c', '#3498db', '#9b59b6'])
    plt.title('Distribución de Métricas de Engagement', fontsize=14, fontweight='bold')
    plt.savefig(OUTPUT_DIR / '23_metricas_engagement.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Métricas de engagement")
    
    # 24. Semana vs fin de semana
    weekend = ['Saturday', 'Sunday']
    posts['is_weekend'] = posts['day_of_week'].isin(weekend)
    weekend_counts = posts['is_weekend'].value_counts()
    plt.figure(figsize=(10, 7))
    plt.pie(weekend_counts.values, labels=['Entre Semana', 'Fin de Semana'], autopct='%1.1f%%',
            startangle=90, colors=['#8dd3c7', '#fb8072'])
    plt.title('Posts: Semana vs Fin de Semana', fontsize=14, fontweight='bold')
    plt.savefig(OUTPUT_DIR / '24_semana_vs_finde.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Semana vs fin de semana")
    
    # 25. Resumen estadísticas
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    axes[0, 0].text(0.5, 0.5, f'{len(profiles):,}\nUsuarios',
                   ha='center', va='center', fontsize=48, fontweight='bold')
    axes[0, 0].set_title('Total Usuarios', fontsize=14)
    axes[0, 0].axis('off')
    
    axes[0, 1].text(0.5, 0.5, f'{len(posts):,}\nPosts',
                   ha='center', va='center', fontsize=48, fontweight='bold', color='navy')
    axes[0, 1].set_title('Total Posts', fontsize=14)
    axes[0, 1].axis('off')
    
    avg_posts = posts_per_user.mean()
    axes[1, 0].text(0.5, 0.5, f'{avg_posts:.1f}\nPosts/Usuario',
                   ha='center', va='center', fontsize=40, fontweight='bold', color='green')
    axes[1, 0].set_title('Promedio Posts por Usuario', fontsize=14)
    axes[1, 0].axis('off')
    
    avg_length = posts['text_length'].mean()
    axes[1, 1].text(0.5, 0.5, f'{avg_length:.0f}\nCaracteres',
                   ha='center', va='center', fontsize=40, fontweight='bold', color='purple')
    axes[1, 1].set_title('Longitud Promedio Posts', fontsize=14)
    axes[1, 1].axis('off')
    
    plt.suptitle('Resumen de Estadísticas', fontsize=20, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '25_resumen_estadisticas.png', dpi=300, bbox_inches='tight')
    plt.close()
    count += 1
    print(f"✓ {count}. Resumen estadísticas")
    
    print("\n" + "=" * 60)
    print(f"✅ {count} gráficos generados en: {OUTPUT_DIR.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    main()

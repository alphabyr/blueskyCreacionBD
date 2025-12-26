"""Verificar la discrepancia entre profiles y posts"""
import json

print("=" * 80)
print("ANÁLISIS DE ARCHIVOS")
print("=" * 80)

# Cargar profiles_to_scan.json
print("\n📖 Cargando profiles_to_scan.json...")
with open('../almacen/profiles_to_scan.json', 'r', encoding='utf-8') as f:
    profiles = json.load(f)

total_profiles = len(profiles)
print(f"✓ Total perfiles en profiles_to_scan.json: {total_profiles:,}")

# Obtener DIDs de profiles
profile_dids = set()
for profile in profiles:
    if 'did' in profile:
        profile_dids.add(profile['did'])

print(f"✓ DIDs únicos en profiles: {len(profile_dids):,}")

# Cargar posts_usuarios.json
print("\n📖 Cargando posts_usuarios.json...")
with open('../almacen/posts_usuarios.json', 'r', encoding='utf-8') as f:
    posts_data = json.load(f)

total_users_in_posts = len(posts_data)
print(f"✓ Total usuarios en posts_usuarios.json: {total_users_in_posts:,}")

# Obtener DIDs de posts
post_dids = set(posts_data.keys())
print(f"✓ DIDs únicos en posts: {len(post_dids):,}")

# Calcular diferencias
print(f"\n" + "=" * 80)
print("ANÁLISIS DE DIFERENCIAS")
print("=" * 80)

faltantes = profile_dids - post_dids
print(f"\n⚠️  Usuarios en profiles pero NO en posts: {len(faltantes):,}")
print(f"❌ Diferencia: {len(faltantes):,} usuarios sin datos de posts")

if len(faltantes) > 0:
    print(f"\n💡 Esto significa que de los {total_profiles:,} perfiles:")
    print(f"   • {total_users_in_posts:,} tienen datos de posts ({total_users_in_posts/total_profiles*100:.1f}%)")
    print(f"   • {len(faltantes):,} NO tienen datos de posts ({len(faltantes)/total_profiles*100:.1f}%)")
    
    # Contar posts reales
    total_posts = sum(len(user_data.get('posts', [])) for user_data in posts_data.values())
    print(f"\n📊 De los {total_users_in_posts:,} usuarios con datos:")
    print(f"   • Total de posts: {total_posts:,}")
    
    usuarios_con_posts = sum(1 for user_data in posts_data.values() 
                            if len(user_data.get('posts', [])) > 0)
    print(f"   • Usuarios con al menos 1 post: {usuarios_con_posts:,}")
    print(f"   • Usuarios sin posts (array vacío): {total_users_in_posts - usuarios_con_posts:,}")

# ¿Los DIDs de posts están en profiles?
posts_no_en_profiles = post_dids - profile_dids
if len(posts_no_en_profiles) > 0:
    print(f"\n⚠️  Usuarios en posts pero NO en profiles: {len(posts_no_en_profiles):,}")

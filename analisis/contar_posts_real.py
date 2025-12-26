"""Script para contar exactamente cuántos posts hay en el archivo JSON original"""
import json

# Cargar el archivo JSON original
print("📖 Cargando posts_usuarios.json...")
with open('../almacen/posts_usuarios.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"\n{'='*80}")
print("CONTEO DETALLADO DE POSTS")
print(f"{'='*80}\n")

# Contar usuarios
total_usuarios = len(data)
print(f"✓ Total usuarios en el archivo: {total_usuarios:,}")

# Contar posts de diferentes formas
total_posts = 0
usuarios_con_posts = 0
usuarios_sin_posts = 0
posts_por_usuario = []

for user_did, user_data in data.items():
    if isinstance(user_data, dict) and 'posts' in user_data:
        posts = user_data['posts']
        if isinstance(posts, list):
            num_posts = len(posts)
            total_posts += num_posts
            posts_por_usuario.append(num_posts)
            if num_posts > 0:
                usuarios_con_posts += 1
            else:
                usuarios_sin_posts += 1
    else:
        usuarios_sin_posts += 1

print(f"✓ Usuarios con posts: {usuarios_con_posts:,}")
print(f"✓ Usuarios sin posts: {usuarios_sin_posts:,}")
print(f"\n{'='*80}")
print(f"🎯 TOTAL DE POSTS EN EL ARCHIVO JSON: {total_posts:,}")
print(f"{'='*80}\n")

# Estadísticas
if posts_por_usuario:
    print(f"📊 Estadísticas de posts por usuario:")
    print(f"   • Mínimo: {min(posts_por_usuario)}")
    print(f"   • Máximo: {max(posts_por_usuario)}")
    print(f"   • Promedio: {sum(posts_por_usuario)/len(posts_por_usuario):.2f}")

# Verificar el archivo JSONL
print(f"\n{'='*80}")
print("VERIFICACIÓN DEL ARCHIVO JSONL")
print(f"{'='*80}\n")

with open('../almacen/posts_usuarios.jsonl', 'r', encoding='utf-8') as f:
    lineas_jsonl = sum(1 for _ in f)

print(f"✓ Líneas en posts_usuarios.jsonl: {lineas_jsonl:,}")

if lineas_jsonl == total_posts:
    print(f"\n✅ CORRECTO: El archivo JSONL tiene el mismo número de posts que el JSON")
else:
    print(f"\n❌ ERROR: Discrepancia detectada!")
    print(f"   JSON original: {total_posts:,} posts")
    print(f"   JSONL generado: {lineas_jsonl:,} líneas")
    print(f"   Diferencia: {abs(total_posts - lineas_jsonl):,} posts")

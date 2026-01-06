#!/usr/bin/env python3
"""
Script de verificación de seguridad para el proyecto Bluesky.
Verifica la integridad de los modelos y configuraciones.
"""
import sys
from pathlib import Path

# Añadir directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from seguridad.secure_model_handler import SecureModelHandler


def verificar_modelos():
    """Verifica la integridad de todos los modelos guardados"""
    print("=" * 80)
    print("🔒 VERIFICACIÓN DE SEGURIDAD - MODELOS ML")
    print("=" * 80)
    
    modelos_dir = Path(__file__).parent / 'prediccion' / 'modelos'
    
    if not modelos_dir.exists():
        print("\n⚠️  No se encontró la carpeta de modelos.")
        print("   Entrena el modelo primero: python prediccion/scripts/2_entrenar_modelo.py")
        return False
    
    handler = SecureModelHandler(modelos_dir)
    
    # Verificar todos los modelos
    print("\n📋 Verificando integridad de archivos...")
    resultados = handler.verificar_todos()
    
    if not resultados:
        print("\n⚠️  No se encontraron modelos para verificar.")
        return False
    
    print()
    tiene_errores = False
    for resultado in resultados:
        print(f"  {resultado['estado']} {resultado['archivo']}")
        print(f"     → {resultado['mensaje']}")
        
        if resultado['estado'] in ['❌ FALTA', '⚠️ MODIFICADO']:
            tiene_errores = True
    
    print("\n" + "-" * 80)
    
    if tiene_errores:
        print("\n🔴 ALERTA: Se detectaron problemas de integridad")
        print("\n🛡️  ACCIONES RECOMENDADAS:")
        print("  1. Si modificaste los modelos manualmente, vuelve a entrenar:")
        print("     → python prediccion/scripts/2_entrenar_modelo.py")
        print("  2. Si NO modificaste nada, puede ser un ataque. Elimina y reentrena:")
        print("     → rm -rf prediccion/modelos/")
        print("     → python prediccion/scripts/2_entrenar_modelo.py")
        return False
    else:
        print("\n✅ VERIFICACIÓN EXITOSA: Todos los modelos son íntegros")
        return True


def listar_modelos():
    """Lista todos los modelos con sus checksums"""
    print("\n" + "=" * 80)
    print("📦 MODELOS ALMACENADOS")
    print("=" * 80)
    
    modelos_dir = Path(__file__).parent / 'prediccion' / 'modelos'
    
    if not modelos_dir.exists():
        print("\n⚠️  No se encontró la carpeta de modelos.")
        return
    
    handler = SecureModelHandler(modelos_dir)
    modelos = handler.listar_modelos()
    
    if not modelos:
        print("\n⚠️  No se encontraron modelos.")
        return
    
    print()
    for modelo in modelos:
        print(f"  📄 {modelo['nombre']}")
        print(f"     Tamaño: {modelo['tamanio_bytes']:,} bytes")
        print(f"     Checksum: {modelo['checksum']}")
        print()


def verificar_permisos():
    """Verifica los permisos de archivos sensibles"""
    print("=" * 80)
    print("🔐 VERIFICACIÓN DE PERMISOS")
    print("=" * 80)
    
    # Archivos que deben tener permisos restrictivos
    archivos_sensibles = [
        'almacen/posts_usuarios.json',
        'almacen/profiles_to_scan.json',
        'prediccion/modelos/bot_detector.pkl',
        'prediccion/modelos/feature_scaler.pkl',
        'prediccion/modelos/feature_columns.pkl',
    ]
    
    print("\n📋 Verificando permisos de archivos sensibles...")
    print()
    
    import stat
    import os
    
    problemas = []
    
    for archivo in archivos_sensibles:
        ruta = Path(__file__).parent / archivo
        
        if not ruta.exists():
            continue
        
        # Obtener permisos
        permisos = oct(stat.S_IMODE(ruta.stat().st_mode))
        
        # Los archivos deberían ser 0o600 (solo propietario)
        if permisos != '0o600':
            print(f"  ⚠️  {archivo}")
            print(f"     Permisos actuales: {permisos} (debería ser 0o600)")
            print(f"     Corregir: chmod 600 {archivo}")
            print()
            problemas.append(archivo)
        else:
            print(f"  ✓ {archivo} - Permisos correctos ({permisos})")
    
    print("\n" + "-" * 80)
    
    if problemas:
        print(f"\n⚠️  {len(problemas)} archivos con permisos inseguros")
        print("\n🛡️  Para corregir todos a la vez:")
        print("  chmod 600 " + " ".join(problemas))
        return False
    else:
        print("\n✅ Todos los archivos tienen permisos seguros")
        return True


def main():
    """Ejecuta todas las verificaciones de seguridad"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "AUDITORÍA DE SEGURIDAD" + " " * 36 + "║")
    print("║" + " " * 20 + "Proyecto Bluesky" + " " * 41 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    verificaciones = []
    
    # Verificar modelos
    verificaciones.append(("Integridad de modelos", verificar_modelos()))
    
    # Listar modelos
    listar_modelos()
    
    # Verificar permisos
    verificaciones.append(("Permisos de archivos", verificar_permisos()))
    
    # Resumen
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE AUDITORÍA")
    print("=" * 80)
    print()
    
    todas_ok = True
    for nombre, resultado in verificaciones:
        if resultado:
            print(f"  ✅ {nombre}")
        else:
            print(f"  ❌ {nombre}")
            todas_ok = False
    
    print("\n" + "=" * 80)
    
    if todas_ok:
        print("\n🎉 TODAS LAS VERIFICACIONES PASARON")
        print("   El sistema está seguro y listo para usar.")
        return 0
    else:
        print("\n⚠️  ALGUNAS VERIFICACIONES FALLARON")
        print("   Revisa los mensajes anteriores y toma las acciones recomendadas.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

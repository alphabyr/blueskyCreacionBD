# Interfaz web (simple)

Esta carpeta contiene una interfaz web pequena en Flask para ejecutar el predictor de bots de forma interactiva.

Como ejecutarla (desarrollo):

- Activa el entorno virtual del proyecto (usamos `.venv` en la raiz del repositorio):
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  export BSKY_HANDLE=your_handle
  export BSKY_APP_PASSWORD=your_app_password
  python web/app.py
  # abre http://127.0.0.1:5000
  ```

Seguridad y notas:
- La interfaz web usa el mismo codigo de carga de modelos que `prediccion/scripts/3_predecir.py` y
  respeta los checksums de SecureModelHandler. Mantener `prediccion/modelos` protegido.
- Esta interfaz esta pensada solo para uso local. Si la despliegas, agrega autenticacion y HTTPS.

Solucion de problemas
- Si ves `ModuleNotFoundError: No module named 'prediccion'` al usar la web:
  - Asegurate de activar el entorno virtual (`source .venv/bin/activate`).
  - Ejecuta la app desde la raiz del repositorio (por ejemplo: `python web/app.py`), o como modulo: `python -m web.app`.
  - Asegura que la raiz del proyecto este en `PYTHONPATH` (la app intenta agregarla automaticamente).

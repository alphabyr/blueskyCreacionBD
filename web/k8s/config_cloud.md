# Instrucciones para construir la imagen (Dockerfile en el root del repo)

1) Ingresa al root del repositorio.

2) Build de la imagen:
   docker build -t bluesky-web:latest -f Dockerfile .

3) (Opcional) Verifica la imagen creada:
   docker images | grep bluesky-web

# Sube la imagen creada a la plataforma Kubernetes

Por ejemplo, este es el comando para subir la imagen a un cluster de Kubernetes Kind:

kind load docker-image bluesky-web:latest


# Instrucciones para correr el manifest de Kubernetes

1) Aplica el manifiesto:
   kubectl apply -f web/k8s/bluesky-web-all.yaml

2) Verifica recursos:
   kubectl get secrets,deployment,service -l app=bluesky-web

# Recursos configurados en el manifest

- Secret "bluesky-creds": almacena BSKY_HANDLE y BSKY_APP_PASSWORD como variables de entorno.
- Deployment "bluesky-web":
  - 3 replicas del contenedor "web".
  - Imagen: bluesky-web:latest.
  - Expone el puerto 5000 dentro del contenedor.
  - Usa el Secret para inyectar variables de entorno.
  - Probes de readiness y liveness en /healthz:5000.
- Service "bluesky-web":
  - Tipo NodePort, expone el servicio en el puerto 80 y lo mapea a 5000.
  - NodePort 30080 para acceso externo (segun el nodo/cluster).

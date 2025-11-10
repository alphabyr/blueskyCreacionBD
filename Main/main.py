# main.py: Ejemplo de uso de la clase datosUsuario

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from usuarios.info import datosUsuario
from usuarios.post import BlueskyPostsFetcher

class MainApp:
	def __init__(self, bsky_handle=None, bsky_app_password=None, target_account='bsky.app', profile_limit=1000, page_limit=100, output_filename=None):
		self.bsky_handle = bsky_handle
		self.bsky_app_password = bsky_app_password
		self.target_account = target_account
		self.profile_limit = profile_limit
		self.page_limit = page_limit
		# Guardar el JSON en la carpeta 'almacen'
		if output_filename is None:
			output_filename = os.path.join('almacen', 'profiles_to_scan.json')
		else:
			output_filename = os.path.join('almacen', output_filename) if not output_filename.startswith('almacen'+os.sep) else output_filename
		# Crear la carpeta si no existe
		os.makedirs(os.path.dirname(output_filename), exist_ok=True)
		self.output_filename = output_filename
		self.fetcher = datosUsuario(self.bsky_handle, self.bsky_app_password)

	def run(self):
		try:
			self.fetcher.login()
			profiles = self.fetcher.fetch_followers(
				target_account_handle=self.target_account,
				profile_limit=self.profile_limit,
				page_limit=self.page_limit
			)
			self.fetcher.save_profiles(profiles, output_filename=self.output_filename)
			# Ejecutar el proceso de posts después de guardar los perfiles
			print("\n--- Iniciando extracción de posts de usuarios ---")
			posts_fetcher = BlueskyPostsFetcher(
				handle=self.bsky_handle,
				app_password=self.bsky_app_password,
				input_file=os.path.basename(self.output_filename), # solo el nombre, ya que la clase añade 'almacen/'
				output_file=None # None para usar el nombre por defecto 'posts_usuarios.json'
			)
			posts_fetcher.run()
		except Exception as e:
			print(f"Error en el proceso: {e}")

if __name__ == "__main__":
	app = MainApp()
	app.run()

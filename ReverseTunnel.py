import os
import json
from sshtunnel import SSHTunnelForwarder
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import confirm
import time

# Ruta del archivo de configuración
config_file_path = os.path.expanduser("~/Documents/Hircoir_Data/ReverseTunnel/config.json")

# Valores por defecto
default_config = {
    "vps_host": "serveo.net",
    "ssh_port": 22,
    "vps_user": "root",
    "vps_password": "root",
    "local_port": 11434,
    "vps_port": 11434
}

# Función para cargar configuración desde el archivo
def load_config():
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as file:
            return json.load(file)
    return default_config.copy()

# Función para guardar configuración en el archivo
def save_config(config):
    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
    with open(config_file_path, "w") as file:
        json.dump(config, file, indent=4)

# Función para solicitar configuración al usuario
def get_config(config):
    print("\n--- Configuración del túnel inverso ---")
    config["vps_host"] = prompt("Dirección IP/Host del VPS [serveo.net]: ", default=config["vps_host"])
    config["ssh_port"] = int(prompt("Puerto SSH del VPS [22]: ", default=str(config["ssh_port"])))
    config["vps_user"] = prompt("Usuario para el VPS [root]: ", default=config["vps_user"])
    config["vps_password"] = prompt("Contraseña para el VPS [root]: ", default=config["vps_password"], is_password=True)
    config["local_port"] = int(prompt("Puerto local de tu API [11434]: ", default=str(config["local_port"])))
    config["vps_port"] = int(prompt("Puerto en el VPS para tu API [11434]: ", default=str(config["vps_port"])))
    return config

# Intentar crear el túnel
def create_tunnel(config):
    retry_delay = 5
    retry_count = 0

    while True:
        try:
            with SSHTunnelForwarder(
                (config["vps_host"], config["ssh_port"]),
                ssh_username=config["vps_user"],
                ssh_password=config["vps_password"],
                remote_bind_address=('127.0.0.1', config["vps_port"]),
                local_bind_address=('127.0.0.1', config["local_port"])
            ) as tunnel:
                print(f"\nTúnel creado: {config['vps_host']}:{config['vps_port']} -> localhost:{config['local_port']}")
                print("Presiona Enter para cerrar el túnel o 'e' para editar los datos y reiniciar el túnel.")
                while True:
                    user_input = input().lower()
                    if user_input == 'e':
                        return False
                    else:
                        print("Cerrando túnel...")
                        return True
        except Exception as e:
            retry_count += 1
            print(f"\nError al conectar: {e}")
            print(f"Reintentando en {retry_delay} segundos... (Intento #{retry_count})")
            time.sleep(retry_delay)

# Bucle principal
config = load_config()

# Instrucciones para el usuario
print("\nEste script sirve para exponer un puerto de una API o web app interna de un servidor remoto a tu computadora.")
print("Te permite acceder a ella desde localhost, lo que es útil, por ejemplo, para conectarte a servidores con 'ollama serve'.")

while True:
    config = get_config(config)
    print("\n--- Resumen de configuración ---")
    for key, value in config.items():
        print(f"{key}: {value}")

    if confirm("\n¿Son correctos estos datos? (y/n)"):
        save_config(config)
        if create_tunnel(config):
            break

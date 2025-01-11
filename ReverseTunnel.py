import os
import json
import base64
import signal
import threading
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sshtunnel import SSHTunnelForwarder
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import confirm, radiolist_dialog
import time

class TunnelManager:
    def __init__(self, config):
        self.config = config
        self.tunnel = None
        self.should_run = True
        self.is_connected = False
        self._lock = threading.Lock()

    def start(self):
        """Start the tunnel and maintain connection"""
        self.should_run = True
        while self.should_run:
            try:
                with self._lock:
                    if self.tunnel is not None:
                        try:
                            self.tunnel.stop()
                        except:
                            pass
                    
                    self.tunnel = SSHTunnelForwarder(
                        (self.config["vps_host"], self.config["ssh_port"]),
                        ssh_username=self.config["vps_user"],
                        ssh_password=self.config["vps_password"],
                        remote_bind_address=('127.0.0.1', self.config["vps_port"]),
                        local_bind_address=('127.0.0.1', self.config["local_port"]),
                        mute_exceptions=True
                    )
                    self.tunnel.start()

                if not self.is_connected:
                    print(f"\nTúnel creado: {self.config['vps_host']}:{self.config['vps_port']} -> localhost:{self.config['local_port']}")
                    print("Presiona Ctrl+C para cerrar el túnel.")
                    self.is_connected = True

                # Check tunnel status periodically
                while self.should_run and self.tunnel.is_active:
                    time.sleep(1)

                if not self.tunnel.is_active and self.should_run:
                    print("\nTúnel desconectado. Intentando reconectar...")
                    self.is_connected = False
                    time.sleep(5)  # Wait before reconnecting

            except Exception as e:
                print(f"\nError en el túnel: {e}")
                print("Intentando reconectar en 5 segundos...")
                self.is_connected = False
                time.sleep(5)

    def stop(self):
        """Stop the tunnel gracefully"""
        self.should_run = False
        with self._lock:
            if self.tunnel is not None:
                try:
                    self.tunnel.stop()
                except:
                    pass

class ConnectionManager:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/Documents/Hircoir_Data/ReverseTunnel")
        self.config_file = os.path.join(self.config_dir, "connections.json")
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        self.key_file = os.path.join(self.config_dir, "key.bin")
        self.fernet = self._setup_encryption()
        self.connections = self._load_connections()
        self.settings = self._load_settings()
        self.current_tunnel = None
        self.tunnel_thread = None

    def _setup_encryption(self):
        """Setup encryption key or load existing one"""
        os.makedirs(self.config_dir, exist_ok=True)
        
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                key = f.read()
        else:
            salt = b"ReverseTunnel"
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(b"ReverseTunnelSecretKey"))
            with open(self.key_file, "wb") as f:
                f.write(key)
        
        return Fernet(key)

    def _load_connections(self):
        """Load saved connections from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                encrypted_data = json.load(f)
                connections = {}
                for name, data in encrypted_data.items():
                    connections[name] = {
                        **data,
                        "vps_password": self.decrypt_password(data["vps_password"])
                    }
                return connections
        return {}

    def _load_settings(self):
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                return json.load(f)
        return {
            "auto_connect": False,
            "default_connection": None
        }

    def _save_settings(self):
        """Save settings to file"""
        with open(self.settings_file, "w") as f:
            json.dump(self.settings, f, indent=4)

    def _save_connections(self):
        """Save connections to file with encrypted passwords"""
        encrypted_data = {}
        for name, data in self.connections.items():
            encrypted_data[name] = {
                **data,
                "vps_password": self.encrypt_password(data["vps_password"])
            }
        
        with open(self.config_file, "w") as f:
            json.dump(encrypted_data, f, indent=4)

    def encrypt_password(self, password):
        """Encrypt a password"""
        return self.fernet.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password):
        """Decrypt a password"""
        return self.fernet.decrypt(encrypted_password.encode()).decode()

    def add_connection(self):
        """Add a new connection configuration"""
        try:
            print("\n--- Nueva Conexión ---")
            print("Presiona Ctrl+C en cualquier momento para volver al menú principal")
            
            name = prompt("Nombre de la conexión: ")
            
            while name in self.connections:
                print("Este nombre ya existe. Por favor, elige otro.")
                name = prompt("Nombre de la conexión: ")

            config = {
                "vps_host": prompt("Dirección IP/Host del VPS [serveo.net]: ", default="serveo.net"),
                "ssh_port": int(prompt("Puerto SSH del VPS [22]: ", default="22")),
                "vps_user": prompt("Usuario para el VPS [root]: ", default="root"),
                "vps_password": prompt("Contraseña para el VPS: ", is_password=True),
                "local_port": int(prompt("Puerto local de tu API [11434]: ", default="11434")),
                "vps_port": int(prompt("Puerto en el VPS para tu API [11434]: ", default="11434"))
            }

            self.connections[name] = config
            self._save_connections()
            print(f"\nConexión '{name}' guardada exitosamente.")

            if confirm("¿Deseas establecer esta conexión como predeterminada para auto-conexión?"):
                self.settings["default_connection"] = name
                self._save_settings()
                print(f"Conexión '{name}' establecida como predeterminada.")

        except KeyboardInterrupt:
            print("\nCreación cancelada. Volviendo al menú principal...")
            return

    def edit_connection(self):
        """Edit an existing connection"""
        if not self.connections:
            print("No hay conexiones para editar.")
            return

        try:
            print("\n--- Editar Conexión ---")
            print("Presiona Ctrl+C en cualquier momento para volver al menú principal")
            
            connection = self.select_connection()
            if not connection:
                return

            old_name = next(name for name, conf in self.connections.items() if conf == connection)
            
            try:
                print(f"\nEditando conexión: {old_name}")
                print("Deja en blanco para mantener el valor actual")

                # Ask for new name
                new_name = prompt(f"Nuevo nombre [{old_name}]: ").strip()
                if new_name and new_name != old_name:
                    if new_name in self.connections:
                        print("Este nombre ya existe. La conexión mantendrá su nombre original.")
                        new_name = old_name
                else:
                    new_name = old_name

                # Ask for new connection details
                new_config = {
                    "vps_host": prompt(f"Dirección IP/Host del VPS [{connection['vps_host']}]: ", default=connection['vps_host']).strip(),
                    "ssh_port": int(prompt(f"Puerto SSH del VPS [{connection['ssh_port']}]: ", default=str(connection['ssh_port']))),
                    "vps_user": prompt(f"Usuario para el VPS [{connection['vps_user']}]: ", default=connection['vps_user']).strip(),
                    "vps_password": prompt("Nueva contraseña para el VPS (deja en blanco para mantener la actual): ", is_password=True).strip() or connection['vps_password'],
                    "local_port": int(prompt(f"Puerto local de tu API [{connection['local_port']}]: ", default=str(connection['local_port']))),
                    "vps_port": int(prompt(f"Puerto en el VPS para tu API [{connection['vps_port']}]: ", default=str(connection['vps_port'])))
                }

                # Update connection
                if old_name != new_name:
                    del self.connections[old_name]
                    # Update default connection name if necessary
                    if self.settings["default_connection"] == old_name:
                        self.settings["default_connection"] = new_name
                        self._save_settings()

                self.connections[new_name] = new_config
                self._save_connections()
                print(f"\nConexión '{new_name}' actualizada exitosamente.")

            except KeyboardInterrupt:
                print("\nEdición cancelada. Volviendo al menú principal...")
                return
            except ValueError as e:
                print(f"\nError: {str(e)}")
                print("La conexión no fue modificada.")
                return

        except KeyboardInterrupt:
            print("\nVolviendo al menú principal...")
            return

    def select_connection(self):
        """Show dialog to select a connection"""
        if not self.connections:
            print("No hay conexiones guardadas.")
            return None

        try:
            choices = [(name, name) for name in self.connections.keys()]
            result = radiolist_dialog(
                title="Seleccionar Conexión",
                text="Elige una conexión:",
                values=choices
            ).run()

            return self.connections.get(result) if result else None
        except KeyboardInterrupt:
            print("\nSelección cancelada.")
            return None

    def delete_connection(self):
        """Delete a saved connection"""
        if not self.connections:
            print("No hay conexiones para eliminar.")
            return

        try:
            connection = self.select_connection()
            if connection:
                name = next(name for name, conf in self.connections.items() if conf == connection)
                if confirm(f"¿Estás seguro de que deseas eliminar la conexión '{name}'?"):
                    # If this is the default connection, remove it from settings
                    if self.settings["default_connection"] == name:
                        self.settings["default_connection"] = None
                        self._save_settings()
                    
                    del self.connections[name]
                    self._save_connections()
                    print(f"\nConexión '{name}' eliminada exitosamente.")
        except KeyboardInterrupt:
            print("\nEliminación cancelada. Volviendo al menú principal...")
            return

    def toggle_auto_connect(self):
        """Toggle auto-connect feature"""
        try:
            if self.settings["auto_connect"]:
                # Si está activado, lo desactivamos
                self.settings["auto_connect"] = False
                self.settings["default_connection"] = None
                self._save_settings()
                print("\nAuto-conexión desactivada.")
            else:
                # Si está desactivado, lo activamos y pedimos la conexión predeterminada
                if not self.connections:
                    print("\nNo hay conexiones guardadas. Crea una conexión primero.")
                    return

                print("\n--- Configurar Auto-conexión ---")
                print("Selecciona la conexión predeterminada para auto-conexión:")
                
                connection = self.select_connection()
                if connection:
                    name = next(name for name, conf in self.connections.items() if conf == connection)
                    self.settings["auto_connect"] = True
                    self.settings["default_connection"] = name
                    self._save_settings()
                    print(f"\nAuto-conexión activada con '{name}' como conexión predeterminada.")
                else:
                    print("\nNo se seleccionó ninguna conexión. Auto-conexión no activada.")

        except KeyboardInterrupt:
            print("\nOperación cancelada. Volviendo al menú principal...")
            return

    def create_tunnel(self, config):
        """Create and maintain SSH tunnel"""
        if self.tunnel_thread and self.tunnel_thread.is_alive():
            print("\nYa hay un túnel activo. Ciérralo primero.")
            return

        tunnel_manager = TunnelManager(config)
        
        def signal_handler(signum, frame):
            print("\nCerrando túnel...")
            tunnel_manager.stop()
        
        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            tunnel_manager.start()
        except KeyboardInterrupt:
            tunnel_manager.stop()
        finally:
            # Restore default signal handler
            signal.signal(signal.SIGINT, signal.default_int_handler)

    def auto_connect(self):
        """Attempt to auto-connect using default connection"""
        if not self.settings["auto_connect"] or not self.settings["default_connection"]:
            return

        default_config = self.connections.get(self.settings["default_connection"])
        if default_config:
            print(f"\nConectando automáticamente a '{self.settings['default_connection']}'...")
            self.create_tunnel(default_config)

def main():
    manager = ConnectionManager()
    
    # Try auto-connect first
    manager.auto_connect()
    
    print("\n🚀 ReverseTunnel - Gestor de Conexiones SSH")
    print("==========================================")
    
    while True:
        print("\nOpciones:")
        print("1. Crear nueva conexión")
        print("2. Conectar a un servidor")
        print("3. Eliminar conexión")
        print("4. Editar conexión")
        print(f"5. {'Desactivar' if manager.settings['auto_connect'] else 'Activar'} auto-conexión")
        print("6. Salir")
        
        try:
            choice = prompt("\nSelecciona una opción (1-6): ")
            
            if choice == "1":
                manager.add_connection()
            elif choice == "2":
                config = manager.select_connection()
                if config:
                    manager.create_tunnel(config)
            elif choice == "3":
                manager.delete_connection()
            elif choice == "4":
                manager.edit_connection()
            elif choice == "5":
                manager.toggle_auto_connect()
            elif choice == "6":
                print("\n¡Hasta luego!")
                break
            else:
                print("\nOpción no válida. Por favor, intenta de nuevo.")
        except KeyboardInterrupt:
            print("\nOperación cancelada. Volviendo al menú principal...")
            continue

if __name__ == "__main__":
    main()
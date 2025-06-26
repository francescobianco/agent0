#!/usr/bin/env python3
"""
Software Auto-Adattivo con Server Telnet
Un programma che può modificare il proprio codice e accetta connessioni via telnet
Connessione: telnet localhost 2323 oppure nc localhost 2323
"""

import os
import sys
import inspect
import requests
import json
import importlib
import types
import socket
import threading
import select
from datetime import datetime
import pickle
import time

# Porta convenzionale per chat testuali (evita la 23 che richiede privilegi root)
DEFAULT_PORT = 2323

class AdaptiveSoftware:
    def __init__(self):
        """Inizializza il software adattivo"""
        self.version = "2.0.0"
        self.created_at = datetime.now()
        self.modifications_count = 0
        self.data_storage = {}
        self.state_file = "adaptive_state.pkl"
        self.server_socket = None
        self.clients = []  # Lista dei client connessi
        self.running = False

        # Configurazione per l'API di OpenAI
        self.api_key = os.getenv('OPENAI_API_KEY', 'your-api-key-here')
        self.api_url = "https://api.openai.com/v1/chat/completions"

        # Carica stato precedente se esiste
        self.load_persistent_state()

        # Dati iniziali (se non caricati)
        if not self.data_storage:
            self.initialize_default_data()

    def initialize_default_data(self):
        """Inizializza alcuni dati di default"""
        self.data_storage = {
            'sample_data': ['Python', 'AI', 'Programmazione'],
            'settings': {'auto_backup': True, 'verbose': True},
            'chat_history': []
        }

    def save_persistent_state(self):
        """Salva lo stato corrente su disco"""
        try:
            state = {
                'version': self.version,
                'created_at': self.created_at,
                'modifications_count': self.modifications_count,
                'data_storage': self.data_storage
            }
            with open(self.state_file, 'wb') as f:
                pickle.dump(state, f)
        except Exception as e:
            self.log(f"❌ Errore nel salvare lo stato: {e}")

    def load_persistent_state(self):
        """Carica lo stato precedente dal disco"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'rb') as f:
                    state = pickle.load(f)

                self.version = state.get('version', self.version)
                self.created_at = state.get('created_at', self.created_at)
                self.modifications_count = state.get('modifications_count', 0)
                self.data_storage = state.get('data_storage', {})

                self.log(f"📥 Stato precedente caricato (v{self.version})")
        except Exception as e:
            self.log(f"⚠️ Impossibile caricare stato precedente: {e}")

    def log(self, message):
        """Log con timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")

    def broadcast_to_clients(self, message, exclude_client=None):
        """Invia un messaggio a tutti i client connessi"""
        disconnected_clients = []
        for client in self.clients:
            if client != exclude_client:
                try:
                    client.send((message + '\r\n').encode('utf-8'))
                except:
                    disconnected_clients.append(client)

        # Rimuovi client disconnessi
        for client in disconnected_clients:
            self.clients.remove(client)

    def handle_client(self, client_socket, client_address):
        """Gestisce una connessione client"""
        client_id = f"{client_address[0]}:{client_address[1]}"
        self.log(f"🔗 Nuovo client connesso: {client_id}")

        try:
            # Messaggio di benvenuto
            welcome_msg = f"""
╔══════════════════════════════════════╗
║    🤖 SOFTWARE AUTO-ADATTIVO v{self.version}     ║
║        Connesso come {client_id}        ║
╚══════════════════════════════════════╝

💡 Comandi disponibili:
  /help     - Mostra questo messaggio
  /info     - Informazioni sul software  
  /data     - Mostra dati memorizzati
  /clients  - Lista client connessi
  /reload   - Ricarica il software
  /quit     - Disconnetti

🎯 Per modificare il software, scrivi la tua richiesta:
   Esempio: "aggiungi una funzione per calcolare numeri primi"

"""
            client_socket.send(welcome_msg.encode('utf-8'))

            buffer = ""
            while self.running:
                try:
                    # Usa select per non bloccare
                    ready = select.select([client_socket], [], [], 1.0)
                    if ready[0]:
                        data = client_socket.recv(1024).decode('utf-8')
                        if not data:
                            break

                        buffer += data

                        # Processa le linee complete
                        while '\n' in buffer or '\r' in buffer:
                            if '\r\n' in buffer:
                                line, buffer = buffer.split('\r\n', 1)
                            elif '\n' in buffer:
                                line, buffer = buffer.split('\n', 1)
                            elif '\r' in buffer:
                                line, buffer = buffer.split('\r', 1)

                            line = line.strip()
                            if line:
                                response = self.process_client_input(line, client_socket, client_id)
                                if response:
                                    client_socket.send((response + '\r\n').encode('utf-8'))

                except socket.timeout:
                    continue
                except Exception as e:
                    self.log(f"❌ Errore con client {client_id}: {e}")
                    break

        except Exception as e:
            self.log(f"❌ Errore gestione client {client_id}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            self.log(f"🔌 Client disconnesso: {client_id}")

    def process_client_input(self, input_text, client_socket, client_id):
        """Processa l'input del client"""
        if input_text.startswith('/'):
            return self.handle_command(input_text, client_socket, client_id)
        else:
            return self.handle_modification_request(input_text, client_socket, client_id)

    def handle_command(self, command, client_socket, client_id):
        """Gestisce i comandi del client"""
        cmd = command.lower().strip()

        if cmd == '/help':
            return """
🆘 COMANDI DISPONIBILI:
  /help     - Mostra questo messaggio
  /info     - Informazioni sul software
  /data     - Mostra dati memorizzati  
  /clients  - Lista client connessi
  /reload   - Ricarica il software
  /quit     - Disconnetti

🔧 ESEMPI DI MODIFICHE:
  "memorizza gli ultimi 10 campioni di scacchi"
  "aggiungi una funzione per numeri primi"
  "implementa un gioco di indovinare il numero"
  "crea un sistema di logging avanzato"
"""

        elif cmd == '/info':
            method_count = len([m for m in dir(self) if not m.startswith('_')])
            return f"""
📋 INFORMAZIONI SISTEMA:
  Versione: {self.version}
  Creato: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}
  Modifiche applicate: {self.modifications_count}
  Metodi disponibili: {method_count}
  Client connessi: {len(self.clients)}
  ID istanza: {id(self)}
  Porta server: {DEFAULT_PORT}
"""

        elif cmd == '/data':
            data_str = "📊 DATI MEMORIZZATI:\n"
            for key, value in self.data_storage.items():
                data_str += f"  {key}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}\n"
            return data_str

        elif cmd == '/clients':
            return f"👥 CLIENT CONNESSI: {len(self.clients)}\n  Indirizzo corrente: {client_id}"

        elif cmd == '/reload':
            self.broadcast_to_clients(f"🔄 {client_id} ha richiesto un reload del sistema", client_socket)
            return "🔄 Ricaricamento del sistema in corso..."

        elif cmd == '/quit':
            return "👋 Arrivederci! Disconnessione in corso..."

        else:
            return f"❓ Comando sconosciuto: {command}. Usa /help per la lista dei comandi."

    def handle_modification_request(self, request, client_socket, client_id):
        """Gestisce le richieste di modifica"""
        self.log(f"🔧 {client_id} richiede: {request}")
        self.broadcast_to_clients(f"🔧 {client_id}: {request}", client_socket)

        # Salva nella chat history
        if 'chat_history' not in self.data_storage:
            self.data_storage['chat_history'] = []

        self.data_storage['chat_history'].append({
            'timestamp': datetime.now().isoformat(),
            'client': client_id,
            'request': request
        })

        try:
            response = "🤔 Elaborando la richiesta...\n"
            response += self.modify_self_for_client(request)
            self.broadcast_to_clients(f"✅ Modifica completata per richiesta di {client_id}", client_socket)
            return response
        except Exception as e:
            error_msg = f"❌ Errore nell'elaborazione: {e}"
            self.log(error_msg)
            return error_msg

    def modify_self_for_client(self, user_prompt):
        """Versione del modify_self adattata per i client"""
        # Crea backup prima delle modifiche
        backup_file = self.backup_current_version()
        if not backup_file:
            return "❌ Impossibile procedere senza backup"

        # Ottieni il nuovo codice dall'LLM
        new_code = self.call_llm(user_prompt)

        if new_code.startswith("Errore"):
            return f"❌ {new_code}"

        # Pulisci il codice
        if "```python" in new_code:
            new_code = new_code.split("```python")[1].split("```")[0].strip()
        elif "```" in new_code:
            new_code = new_code.split("```")[1].strip()

        try:
            # Scrivi il nuovo codice
            current_file = self.get_current_file_path()
            with open(current_file, 'w', encoding='utf-8') as f:
                f.write(new_code)

            return f"✅ Software modificato con successo!\n📁 Backup: {backup_file}\n🔄 Riavvia il server per le modifiche"

        except Exception as e:
            return f"❌ Errore nella scrittura del file: {e}"

    def get_current_code(self):
        """Restituisce il codice sorgente corrente del file"""
        try:
            current_file = inspect.getfile(self.__class__)
            with open(current_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Errore nel leggere il codice: {e}"

    def get_current_file_path(self):
        """Restituisce il percorso del file corrente"""
        return inspect.getfile(self.__class__)

    def backup_current_version(self):
        """Crea un backup della versione corrente"""
        try:
            current_file = self.get_current_file_path()
            backup_name = f"{current_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            with open(current_file, 'r', encoding='utf-8') as original:
                with open(backup_name, 'w', encoding='utf-8') as backup:
                    backup.write(original.read())

            self.log(f"💾 Backup creato: {backup_name}")
            return backup_name
        except Exception as e:
            self.log(f"❌ Errore nel creare backup: {e}")
            return None

    def call_llm(self, prompt):
        """Chiama il LLM per ottenere suggerimenti di modifica del codice"""
        current_code = self.get_current_code()

        system_prompt = """Sei un assistente AI specializzato nella modifica di codice Python per un software auto-adattivo con server telnet.
        
        REGOLE IMPORTANTI:
        1. Mantieni SEMPRE la struttura base della classe AdaptiveSoftware
        2. Non rimuovere mai i metodi del server (start_server, handle_client, etc.)
        3. Aggiungi nuove funzionalità come metodi della classe
        4. Se richiesto di memorizzare dati, modifica data_storage
        5. Restituisci SOLO il codice Python completo
        6. Mantieni tutti i commenti e la formattazione
        7. Incrementa il numero di versione
        8. Mantieni tutti i meccanismi di rete e client handling"""

        user_message = f"""Richiesta utente: {prompt}

Codice attuale:
```python
{current_code}
```

Modifica il codice per soddisfare la richiesta mantenendo tutte le funzionalità server."""

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_message}
                ],
                'max_tokens': 4000,
                'temperature': 0.3
            }

            response = requests.post(self.api_url, headers=headers, json=data)

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Errore API: {response.status_code} - {response.text}"

        except Exception as e:
            return f"Errore nella chiamata LLM: {e}"

    def start_server(self, port=DEFAULT_PORT):
        """Avvia il server telnet"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', port))
            self.server_socket.listen(5)
            self.running = True

            self.log(f"🚀 Server avviato su porta {port}")
            self.log(f"📞 Connetti con: telnet localhost {port}")
            self.log(f"📞 Oppure con: nc localhost {port}")

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    self.clients.append(client_socket)

                    # Crea un thread per ogni client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()

                except Exception as e:
                    if self.running:
                        self.log(f"❌ Errore accettazione client: {e}")

        except Exception as e:
            self.log(f"❌ Errore avvio server: {e}")
        finally:
            self.stop_server()

    def stop_server(self):
        """Ferma il server"""
        self.running = False
        self.save_persistent_state()

        # Chiudi tutti i client
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.clients.clear()

        # Chiudi il server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        self.log("🛑 Server fermato")

def main():
    """Funzione principale"""
    print("🚀 Avvio Software Auto-Adattivo con Server Telnet")

    # Crea un'istanza del software adattivo
    adaptive_ai = AdaptiveSoftware()

    try:
        # Avvia il server
        adaptive_ai.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Interruzione rilevata")
    finally:
        adaptive_ai.stop_server()
        print("👋 Arrivederci!")

if __name__ == "__main__":
    main()
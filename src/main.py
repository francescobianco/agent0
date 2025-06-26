#!/usr/bin/env python3
"""
Software Auto-Adattivo con Controller Esterno
Un programma che può modificare il proprio codice, controllato da un file esterno
"""

import os
import sys
import inspect
import requests
import json
import importlib
import types
from datetime import datetime
import pickle
import time

class AdaptiveSoftware:
    def __init__(self):
        """Inizializza il software adattivo"""
        self.version = "3.0.0"
        self.created_at = datetime.now()
        self.modifications_count = 0
        self.data_storage = {}
        self.state_file = "adaptive_state.pkl"

        # Configurazione per l'API di OpenAI
        self.api_key = os.getenv('OPENAI_API_KEY', 'your-api-key-here')
        print("🔑 API Key:", self.api_key)
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
            'command_history': []
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

    def process_command(self, command):
        """Process a single command and return response"""
        command = command.strip()

        # Salva comando nella history
        if 'command_history' not in self.data_storage:
            self.data_storage['command_history'] = []

        self.data_storage['command_history'].append({
            'timestamp': datetime.now().isoformat(),
            'command': command
        })

        # Comandi di sistema
        if command == "info":
            return self.show_info()
        elif command == "data":
            return self.show_data()
        elif command == "history":
            return self.show_history()
        elif command == "help":
            return self.show_help()
        elif command in ["exit", "quit"]:
            return None  # Segnala che bisogna uscire
        elif command.startswith("modify:"):
            # Comando di modifica del software
            modification_request = command.split(":", 1)[1]
            return self.handle_modification_request(modification_request)
        elif command.startswith("add_function:"):
            # Aggiunge una nuova funzione
            function_request = command.split(":", 1)[1]
            return self.add_function_request(function_request)
        else:
            return f"Comando non riconosciuto: {command}. Usa 'help' per vedere i comandi disponibili."

    def show_info(self):
        """Mostra informazioni sul sistema"""
        method_count = len([m for m in dir(self) if not m.startswith('_')])
        return f"""
📋 INFORMAZIONI SISTEMA:
  Versione: {self.version}
  Creato: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}
  Modifiche applicate: {self.modifications_count}
  Metodi disponibili: {method_count}
  ID istanza: {id(self)}
"""

    def show_data(self):
        """Mostra dati memorizzati"""
        data_str = "📊 DATI MEMORIZZATI:\n"
        for key, value in self.data_storage.items():
            data_str += f"  {key}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}\n"
        return data_str

    def show_history(self):
        """Mostra cronologia comandi"""
        history = self.data_storage.get('command_history', [])
        if not history:
            return "📜 Nessun comando nella cronologia"

        history_str = "📜 CRONOLOGIA COMANDI (ultimi 10):\n"
        for entry in history[-10:]:
            timestamp = entry['timestamp'][:19].replace('T', ' ')
            history_str += f"  {timestamp}: {entry['command']}\n"
        return history_str

    def show_help(self):
        """Show available commands"""
        help_text = """
🆘 COMANDI DISPONIBILI:
  info                           : Informazioni sul sistema
  data                          : Mostra dati memorizzati
  history                       : Cronologia comandi
  modify:richiesta              : Modifica il software (es: modify:aggiungi calcolo fibonacci)
  add_function:nome             : Aggiunge una funzione specifica
  help                          : Mostra questo aiuto
  exit/quit                     : Esci dal programma

🔧 ESEMPI DI MODIFICHE:
  modify:aggiungi una funzione per calcolare numeri primi
  modify:implementa un gioco di indovinare il numero
  modify:crea un sistema di cache per le risposte
  add_function:fibonacci        : Aggiunge calcolo Fibonacci
  add_function:palindrome       : Aggiunge controllo palindromo
        """
        return help_text.strip()

    def handle_modification_request(self, request):
        """Gestisce le richieste di modifica"""
        self.log(f"🔧 Richiesta modifica: {request}")

        try:
            response = "🤔 Elaborando la richiesta di modifica...\n"
            result = self.modify_self(request)
            return response + result
        except Exception as e:
            error_msg = f"❌ Errore nell'elaborazione: {e}"
            self.log(error_msg)
            return error_msg

    def add_function_request(self, function_name):
        """Aggiunge funzioni predefinite"""
        functions_map = {
            'fibonacci': 'aggiungi una funzione per calcolare la sequenza di Fibonacci',
            'palindrome': 'aggiungi una funzione per verificare se una stringa è palindroma',
            'prime': 'aggiungi una funzione per verificare se un numero è primo',
            'sort': 'aggiungi una funzione per ordinare una lista di numeri',
            'reverse': 'aggiungi una funzione per invertire una stringa',
            'factorial': 'aggiungi una funzione per calcolare il fattoriale'
        }

        if function_name.lower() in functions_map:
            request = functions_map[function_name.lower()]
            return self.handle_modification_request(request)
        else:
            available = ', '.join(functions_map.keys())
            return f"❓ Funzione '{function_name}' non disponibile. Disponibili: {available}"

    def modify_self(self, user_prompt):
        """Modifica il software basandosi sul prompt dell'utente"""
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
            # Verifica sintassi del codice
            compile(new_code, '<string>', 'exec')

            # Scrivi il nuovo codice
            current_file = self.get_current_file_path()
            with open(current_file, 'w', encoding='utf-8') as f:
                f.write(new_code)

            # Incrementa contatore modifiche
            self.modifications_count += 1
            self.save_persistent_state()

            return f"✅ Software modificato con successo!\n📁 Backup: {backup_file}\n🔄 Riavvia per applicare le modifiche"

        except SyntaxError as e:
            return f"❌ Errore di sintassi nel codice generato: {e}"
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

        system_prompt = """Sei un assistente AI specializzato nella modifica di codice Python per un software auto-adattivo.
        
        REGOLE IMPORTANTI:
        1. Mantieni SEMPRE la struttura base della classe AdaptiveSoftware
        2. Non rimuovere mai i metodi core (process_command, modify_self, etc.)
        3. Aggiungi nuove funzionalità come metodi della classe
        4. Se richiesto di memorizzare dati, modifica data_storage
        5. Restituisci SOLO il codice Python completo
        6. Mantieni tutti i commenti e la formattazione
        7. Incrementa il numero di versione in modo appropriato
        8. Aggiungi la nuova funzionalità al process_command se appropriato
        9. Mantieni il metodo run() per l'esecuzione principale"""

        user_message = f"""Richiesta utente: {prompt}

Codice attuale:
```python
{current_code}
```

Modifica il codice per soddisfare la richiesta mantenendo tutte le funzionalità esistenti."""

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

    def run(self):
        """Main execution loop - gestisce prompt e input"""
        print("==================================")
        print(f"   AGENTE AUTO-ADATTIVO v{self.version}")
        print("==================================")
        print("Digita 'help' per vedere i comandi disponibili")
        print(f"Modifiche applicate: {self.modifications_count}")
        print("")

        while True:
            try:
                # Mostra prompt e legge input
                user_input = input("adaptive> ").strip()

                # Ignora input vuoti
                if not user_input:
                    continue

                # Processa il comando
                response = self.process_command(user_input)

                # Se response è None, significa che bisogna uscire
                if response is None:
                    print("Salvataggio stato...")
                    self.save_persistent_state()
                    print("Arrivederci!")
                    sys.exit(0)

                # Stampa la risposta
                print(response)
                print("")

            except KeyboardInterrupt:
                print("\nSalvataggio stato...")
                self.save_persistent_state()
                print("Arrivederci!")
                sys.exit(0)
            except EOFError:
                print("\nSalvataggio stato...")
                self.save_persistent_state()
                print("Arrivederci!")
                sys.exit(0)
            except Exception as e:
                print(f"Errore: {e}")
                self.log(f"Errore runtime: {e}")

def main():
    """Funzione principale"""
    print("🚀 Avvio Software Auto-Adattivo")

    # Crea un'istanza del software adattivo
    adaptive_software = AdaptiveSoftware()

    try:
        # Avvia il loop principale
        adaptive_software.run()
    except Exception as e:
        print(f"Errore critico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Version 3.0 - External controller with self-modification capabilities
import socket
import threading
import importlib

class AdaptiveSoftware:
    def __init__(self):
        self.data_storage = []
        self.server = None
        self.server_thread = None

    def add_function_to_calculate_prime_numbers(self, n):
        """Add a function to calculate prime numbers up to n"""
        def is_prime(num):
            if num < 2:
                return False
            for i in range(2, int(num ** 0.5) + 1):
                if num % i == 0:
                    return False
            return True

        prime_numbers = [num for num in range(2, n+1) if is_prime(num)]
        return prime_numbers

    def add_function_to_identify_even_numbers(self, numbers):
        """Add a function to identify even numbers in a list"""
        even_numbers = [num for num in numbers if num % 2 == 0]
        return even_numbers

    def add_function_to_identify_odd_numbers(self, numbers):
        """Add a function to identify odd numbers in a list"""
        odd_numbers = [num for num in numbers if num % 2 != 0]
        return odd_numbers

    def add_function_to_calculate_average(self, numbers):
        """Add a function to calculate the average of a list of numbers"""
        if len(numbers) == 0:
            return 0
        return sum(numbers) / len(numbers)

    def add_function_to_reverse_string(self, input_string):
        """Add a function to reverse a string"""
        return input_string[::-1]

    def start_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('localhost', 12345))
        self.server.listen(5)
        print("Server started. Waiting for connections...")
        
        self.server_thread = threading.Thread(target=self._server_thread)
        self.server_thread.start()

    def _server_thread(self):
        while True:
            client_socket, client_address = self.server.accept()
            print(f"Connection from {client_address}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client_socket):
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break

            if data == "reload":
                importlib.reload(self)
                response = "Code reloaded successfully!"
            else:
                response = "Invalid command"

            client_socket.send(response.encode('utf-8'))

        client_socket.close()

    def stop_server(self):
        if self.server:
            self.server.close()
        if self.server_thread:
            self.server_thread.join()

# Version 2.1/
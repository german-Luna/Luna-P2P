import socket
import json
from pathlib import Path

class Client:
    def __init__(self, ip, port=5000):
        """
        Initialize a Client object.

        Parameters:
        - ip (str): IP address of the server.
        - port (int): Port number to connect to (default is 5000).
        """
        self.ip = ip
        self.port = port
        self.chunk_size = None
        self.gzip_lvl = None
        self.sock = None

    def start_client(self):
        """
        Start the client by connecting to the server and initiating file transfer.
        """
        self.connect_to_server()

    def connect_to_server(self):
        """
        Connect to the server and initiate the file transfer process.
        """
        # Create a socket and connect to the server
        self.sock = socket.socket()
        self.sock.connect((self.ip, self.port))

        # Receive configuration from the server
        self.receive_configuration(self.sock)

        # Get file information and send the file
        filename = self.get_file_info()
        self.send_file(self.sock, filename)

    def receive_configuration(self, sock):
        """
        Receive and set the configuration parameters from the server.

        Parameters:
        - sock: The socket connected to the server.
        """
        settings = json.loads(sock.recv(2048).decode("UTF-8"))
        self.chunk_size = settings["chunk_size"]
        self.gzip_lvl = settings["gzip_lvl"]

    def get_file_info(self):
        """
        Get user input for the file path and send the filename to the server.

        Returns:
        - str: Filepath entered by the user.
        """
        filepath = input("Filepath: ")
        filename = Path(filepath).name
        self.sock.sendall(bytes(json.dumps({"file_name": filename}), "UTF-8"))
        return filepath

    def send_file(self, sock, filepath):
        """
        Send the file in chunks to the server.

        Parameters:
        - sock: The socket connected to the server.
        - filepath (str): Path to the file to be sent.
        """
        with open(filepath, "rb") as f_in:
            while True:
                data = f_in.read(self.chunk_size)

                if not data:
                    print("Reached end of File")
                    break

                sock.sendall(data)
                print("Sent Chunk")


class Server:
    def __init__(self, ip=None, port=5000, chunk_size=11_048_576, gzip_lvl=9):
        """
        Initialize a Server object.

        Parameters:
        - ip (str): IP address to bind the server to (default is None for localhost).
        - port (int): Port number to bind to (default is 5000).
        - chunk_size (int): Size of data chunks for file transfer (default is 11,048,576 bytes).
        - gzip_lvl (int): Gzip compression level (default is 9).
        """
        self.chunk_size = chunk_size
        self.gzip_lvl = gzip_lvl
        self.sock = None

        if ip is None:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)

        # Create a socket and bind it to the specified address and port
        self.sock = socket.socket()
        self.sock.bind((ip, port))

    def start_server(self):
        """
        Start the server and wait for a client to connect.
        """
        self.sock.listen()
        conn, address = self.sock.accept()
        print("Connection from: " + str(address))

        # Send configuration to the client
        self.send_configuration(conn)

        # Receive file information and receive the file
        answer = self.receive_data(conn)
        file_name = answer["file_name"]
        self.receive_file(conn, file_name)

    def send_configuration(self, conn):
        """
        Send server configuration data to the connected client.

        Parameters:
        - conn: The connection socket to the client.
        """
        config_data = {
            "chunk_size": self.chunk_size,
            "gzip_lvl": self.gzip_lvl
        }
        conn.sendall(bytes(json.dumps(config_data), "UTF-8"))

    def receive_data(self, conn):
        """
        Receive and decode JSON data from the connected client.

        Parameters:
        - conn: The connection socket to the client.

        Returns:
        - dict: Decoded JSON data received from the client.
        """
        data = conn.recv(2048).decode("UTF-8")
        return json.loads(data)

    def receive_file(self, conn, file_name):
        """
        Receive the file in chunks from the connected client.

        Parameters:
        - conn: The connection socket to the client.
        - file_name (str): Name of the file to be received.
        """
        with open(file_name, "ab") as f_out:
            while True:
                data = conn.recv(self.chunk_size)

                if not data:
                    print("Finished Receiving")
                    break

                f_out.write(data)
                print("Wrote Chunk")

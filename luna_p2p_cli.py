import argparse
import sys
import luna_p2p

parser = argparse.ArgumentParser(description="Luna P2P")

mode_group = parser.add_mutually_exclusive_group(required=True)
mode_group.add_argument("--client", action="store_true", help="Enable client mode")
mode_group.add_argument("--server", action="store_true", help="Enable server mode")

parser.add_argument("--ip", required="--client" in sys.argv, help="Server IP in client mode")
parser.add_argument("--port", type=int, help="Port number for communication")

parser.add_argument("--chunk_size", type=int, help="Size of data chunks for file transfer in server mode")
parser.add_argument("--gzip_level", type=int, help="Gzip compression level in server mode")

args = parser.parse_args()

if args.client:
    client = luna_p2p.Client(ip=args.ip, port=args.port)
    client.connect_to_server()

elif args.server:
    server = luna_p2p.Server(ip=args.ip, port=args.port, chunk_size=args.chunk_size, gzip_lvl=args.gzip_level)
    server.start_server()

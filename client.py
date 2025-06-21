# client.py
import socket
import argparse

def run_client(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        print(f"[CLIENT] Connected to {host}:{port}")
        while True:
            prompt = input("You: ")
            if prompt.lower() in ("exit", "quit"):
                print("[CLIENT] Goodbye!")
                break
            sock.sendall(prompt.encode())
            data = sock.recv(65535)
            print(f"AI: {data.decode()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI TCP Client")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Server address to connect to")
    parser.add_argument("--port", type=int, default=5000,
                        help="Server port to connect to")
    args = parser.parse_args()
    run_client(args.host, args.port)

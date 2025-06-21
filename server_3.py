# server.py
import socket
import threading
import argparse
import time
from google import genai
from google.genai import types
from google.genai.errors import ClientError

def generate(prompt_text: str, max_retries: int = 3) -> str:
    client = genai.Client(
        vertexai=True,
        project="hack-the-law25cam-501",
        location="global",
    )

    model = "gemini-2.5-flash"
    contents = [ types.Content(role="user", parts=[ types.Part(text=prompt_text) ]) ]
    config = types.GenerateContentConfig(
        temperature=1,
        top_p=1,
        seed=0,
        max_output_tokens=65535,
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        thinking_config=types.ThinkingConfig(thinking_budget=-1),
    )

    attempt = 0
    while True:
        try:
            result = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=config,
            ):
                print(chunk.text, end="", flush=True)
                result += chunk.text
            print()
            return result

        except ClientError as e:
            code = getattr(e, 'status_code', None)
            if code == 429 or "RESOURCE_EXHAUSTED" in str(e):
                attempt += 1
                if attempt > max_retries:
                    print("[Server][Gemini] Giving up after retries.", flush=True)
                    return ""
                wait = 2 ** attempt
                print(f"[Server][Gemini] Resource exhausted – retrying in {wait}s…", flush=True)
                time.sleep(wait)
            else:
                raise

def handle_receive(conn: socket.socket):
    while True:
        data = conn.recv(4096)
        if not data:
            break
        prompt = data.decode()
        print(f"[Client] {prompt}")
        generate(prompt)

def handle_send(conn: socket.socket):
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        conn.sendall(user_input.encode())
        generate(user_input)

def run_server(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"[Server] Listening on {host}:{port}…")
        conn, _ = s.accept()
        print("[Server] Connected.")
        threading.Thread(target=handle_receive, args=(conn,), daemon=True).start()
        handle_send(conn)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI TCP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Interface to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    args = parser.parse_args()
    run_server(args.host, args.port)

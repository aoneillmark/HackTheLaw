# server.py
from google import genai
from google.genai import types
import socket
import argparse

def generate(prompt_text):
    client = genai.Client(
        vertexai=True,
        project="hack-the-law25cam-501",
        location="global",
    )

    model = "gemini-2.5-flash"
    contents = [
      types.Content(
        role="user",
        parts=[ types.Part(text=prompt_text) ]
      )
    ]

    generate_content_config = types.GenerateContentConfig(
      temperature = 1,
      top_p = 1,
      seed = 0,
      max_output_tokens = 65535,
      safety_settings = [
        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
      ],
      thinking_config = types.ThinkingConfig(thinking_budget=-1),
    )

    response = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        # stream-print exactly as before
        print(chunk.text, end="", flush=True)
        response += chunk.text
    print()  
    return response

def run_server(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, port))
        sock.listen(1)
        print(f"[SERVER] Listening on {host}:{port}…")
        conn, addr = sock.accept()
        with conn:
            print(f"[SERVER] Connected by {addr}")
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                prompt = data.decode()
                print(f"[SERVER] Prompt → {prompt!r}")
                reply = generate(prompt)
                conn.sendall(reply.encode())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI TCP Server")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Interface to bind to")
    parser.add_argument("--port", type=int, default=5000,
                        help="Port to listen on")
    args = parser.parse_args()
    run_server(args.host, args.port)

# scan.py

import time
import json
import yaml
import requests
from urllib.parse import urlparse

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f).get("zap", {})

API_KEY = config.get("api_key", "")
ADDR = config.get("host", "localhost")
PORT = config.get("port", 8080)
BASE = f"http://{ADDR}:{PORT}"

seen_ids = set()

def get_messages():
    url = f"{BASE}/JSON/core/view/messages/"
    params = {"apikey": API_KEY}
    res = requests.get(url, params=params)
    return res.json().get("messages", [])

def get_message_by_id(msg_id):
    url = f"{BASE}/JSON/core/view/message/"
    params = {"id": msg_id, "apikey": API_KEY}
    res = requests.get(url, params=params)
    return res.json().get("message", {})

def extract_content_type(headers):
    for line in headers.splitlines():
        if line.lower().startswith("content-type:"):
            return line.split(":", 1)[1].strip().lower()
    return ''

def extract_path(url):
    try:
        return urlparse(url).path or "/"
    except:
        return "/"

def truncate(value, limit=20):
    return value[:limit] + "..." if len(value) > limit else value

def classify_request(method, headers, body, url):
    content_type = extract_content_type(headers)

    if method in ("POST", "PUT", "PATCH", "DELETE"):
        if "application/json" in content_type:
            return "GRAPHQL", truncate(body)
        elif "application/x-www-form-urlencoded" in content_type:
            return "FORM", truncate(body)
        elif "multipart/form-data" in content_type:
            return "MULTIPART", "[multipart truncated]"
        elif "application/xml" in content_type or body.strip().startswith("<"):
            return "XML", truncate(body)
        else:
            return "RAW", truncate(body)

    if method == "GET" and "?" in url:
        return "URL", truncate(url.split("?", 1)[1])

    return None, None

def monitor_requests(output_file="scan.txt"):
    print(f"[*] Monitoring new traffic on {ADDR}:{PORT}...\n")

    with open(output_file, "w") as f:
        while True:
            try:
                for msg in get_messages():
                    try:
                        msg_id = int(msg.get('id', -1))
                        if msg_id in seen_ids:
                            continue
                        seen_ids.add(msg_id)

                        full = get_message_by_id(msg_id)
                        if not full:
                            continue

                        headers = full.get("requestHeader", "")
                        body = full.get("requestBody", "")

                        try:
                            url = headers.split(" ")[1]
                        except IndexError:
                            url = "/"

                        request_line = headers.splitlines()[0]
                        method = request_line.split(" ")[0].upper() if request_line else ""

                        # Skip uninteresting HTTP methods
                        if method in ["OPTIONS", "HEAD", "TRACE", "CONNECT"]:
                            continue

                        # Skip static assets
                        if any(url.lower().endswith(ext) for ext in ['.js', '.css', '.png', '.jpg', '.svg', '.ico', '.woff', '.ttf']):
                            continue

                        # Skip requests without input
                        if not method or not headers or (not body and "?" not in url):
                            continue

                        rtype, rvalue = classify_request(method, headers, body, url)
                        if not rtype:
                            continue

                        endpoint = extract_path(url)
                        line = f"[ID:{msg_id}]~[{method}]~[{rtype}]~[{rvalue}]~[{endpoint}]"
                        print(line)
                        f.write(line + "\n")

                    except Exception as e:
                        print(f"[!] Error in processing message: {e}")
                time.sleep(2)
            except KeyboardInterrupt:
                print("\n[*] Stopped.")
                break


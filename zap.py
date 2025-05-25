# zap.py
import os
import yaml
import requests

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')


def load_zap_config():
    """Load ZAP settings from config.yaml"""
    with open(CONFIG_PATH, 'r') as f:
        cfg = yaml.safe_load(f) or {}
    zap = cfg.get('zap', {})
    return zap['api_key'], zap['host'], zap['port']


def get_proxies():
    """Return proxies dict for requests based on ZAP host/port"""
    _, host, port = load_zap_config()
    proxy = f"http://{host}:{port}"
    return {'http': proxy, 'https': proxy}


def get_message(id):
    """Retrieve a message from ZAP proxy history by ID"""
    api_key, host, port = load_zap_config()
    url = f"http://{host}:{port}/JSON/core/view/message/"
    resp = requests.get(url, params={'id': id, 'apikey': api_key})
    resp.raise_for_status()
    data = resp.json()
    return data['message']


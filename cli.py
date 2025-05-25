#!/usr/bin/env python3
import argparse
import os
import sys
import yaml
import scan  # <-- New import for scan logic
from scripts.gql_viper.script import run_introspection

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'scripts')
DEFAULT_OUTPUT = os.path.join(SCRIPTS_DIR, 'gql_viper', 'output.txt')

def configure():
    zap = {
        'api_key': input('Enter ZAP API Key: '),
        'host': input('Enter ZAP proxy host [127.0.0.1]: ') or '127.0.0.1',
        'port': int(input('Enter ZAP proxy port [8080]: ') or '8080'),
    }
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump({'zap': zap}, f)
    print(f'[+] Config saved to {CONFIG_PATH}')

def load_config():
    if not os.path.exists(CONFIG_PATH):
        sys.exit("[!] config.yaml not found. Run `python cli.py config` first.")
    cfg = yaml.safe_load(open(CONFIG_PATH))
    zap = cfg.get('zap', {})
    if not all(k in zap for k in ('api_key', 'host', 'port')):
        sys.exit("[!] config.yaml is missing required fields.")
    return cfg

def clone_script(name):
    import shutil, subprocess
    repo = f"https://github.com/gremlin-0x/{name}_viper.git"
    dest = os.path.join(SCRIPTS_DIR, f"{name}_viper")
    if os.path.exists(dest):
        print(f"[*] Removing old {dest}")
        shutil.rmtree(dest)
    print(f"[*] Cloning {repo} → {dest}")
    subprocess.check_call(['git', 'clone', repo, dest])
    print("[+] Clone complete.")

def main():
    parser = argparse.ArgumentParser(prog='aspiti')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Config
    subparsers.add_parser('config', help='Prompt and write ZAP config.yaml')

    # Load
    load = subparsers.add_parser('load', help='Clone helper scripts')
    load.add_argument('name', choices=['gql'])

    # GraphQL
    gql = subparsers.add_parser('gql', help='GraphQL: introspect')
    gql.add_argument('-i', '--id', required=True, type=int, help='ZAP request ID')
    gql.add_argument('-m', '--method', required=True, choices=['GET', 'POST'], help='HTTP method')
    gql.add_argument('-o', '--output', help='Save introspection output to file')
    gql.add_argument('--mode', choices=['inline', 'variables'], default='inline', help='Output mode')

    # Scan
    scan_parser = subparsers.add_parser('scan', help='Start live scan for param-based requests')
    scan_parser.add_argument('-o', '--output', default='scan.txt', help='Output file to save scan results')

    args = parser.parse_args()

    if args.command == 'config':
        configure()
    elif args.command == 'load':
        clone_script(args.name)
    elif args.command == 'gql':
        load_config()
        run_introspection(args.id, args.method, args.output or DEFAULT_OUTPUT, args.mode)
    elif args.command == 'scan':
        load_config()  # ensures config is present and valid
        scan.monitor_requests(output_file=args.output)

if __name__ == '__main__':
    main()


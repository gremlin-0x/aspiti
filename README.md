# aspiti

![ASPITI header](img/header.png)

`aspiti` is a lightweight command-line interface that automates the loading and usage of security tools, with first-class support for the ZAP Proxy API. It is designed as a wrapper to organize, invoke, and interact with security testing scripts—such as the GraphQL-focused [`gql_viper`](https://github.com/gremlin-0x/gql_viper).

## ✨ Features

* Simple CLI interface for configuring and using ZAP with auxiliary tools
* Introspection and replay automation for GraphQL via `gql_viper`
* Automatic script loader (`aspiti load <script>`)
* Real-time proxy history listener with request parameter scanning (`aspiti scan`)
* Keeps your config and tools organized in a portable workspace
* Designed for red teaming and offensive research environments

## 📦 Directory Layout

```
aspiti/
├── cli.py                 # Main CLI entry point
├── config.yaml            # Saved ZAP configuration
├── zap.py                 # ZAP API wrapper for proxying and replaying requests
├── scan.py                # Passive listener for ZAP history
└── scripts/
    └── gql_viper/         # Git-submodule or manually cloned repository
```

## ⚙️ Configuration

To set your ZAP proxy details (host, port, API key):

```bash
python cli.py config
```

This creates or overwrites `config.yaml` with your input.

## 🚀 Usage

### Load helper script (e.g. GraphQL)

```bash
python cli.py load gql
```

This clones the `gql_viper` repository into `./scripts/gql_viper`. Replaces any existing version.

### Run GraphQL introspection (inline)

```bash
python cli.py gql -i <ZAP-Request-ID> -m POST -o output.txt
```

### Run introspection with `variables` mode

```bash
python cli.py gql -i <ZAP-Request-ID> -m POST --mode variables -o output.txt
```

* `-i` ZAP history request ID to clone headers and URL from
* `-m` HTTP method (GET or POST)
* `--mode` can be `inline` (default) or `variables` to structure query with GraphQL-compliant variables object
* `-o` Output file for generated queries (default: `scripts/gql_viper/output.txt`)

### Scan ZAP proxy history in real time

```bash
python cli.py scan
```

This starts a loop that monitors ZAP history entries and prints any request containing parameters in URL query strings or JSON bodies. Useful for passive discovery of interesting traffic during browsing or fuzzing.

## 🧠 Philosophy

`aspiti` was created to serve as the glue between red team tooling and manual ZAP-assisted reconnaissance. It enables repeatable, configurable workflows for exploiting complex API targets—starting with GraphQL introspection.

## 📌 Dependencies

* Python 3.8+
* [ZAP Proxy](https://www.zaproxy.org/) (running and accessible)
* `requests`, `yaml`, `colorama`

## 🔗 Related Projects

* [`gql_viper`](https://github.com/gremlin-0x/gql_viper) – GraphQL introspection and query builder

## 🛪️ License

MIT


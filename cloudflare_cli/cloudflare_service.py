import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

def load_config():
    """
    Load configuration from environment variables, global config file, or local .env.
    Priority: env vars > global config (~/.cloudflare-cli/config.json) > local .env
    """
    config = {}

    # Check environment variables first
    config['api_base'] = os.getenv("CLOUDFLARE_API_BASE", "https://api.cloudflare.com/client/v4")
    config['api_token'] = os.getenv("CLOUDFLARE_API_TOKEN")

    # If token not in env, check global config
    if not config['api_token']:
        config_dir = Path.home() / '.cloudflare-cli'
        config_file = config_dir / 'config.json'
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    global_config = json.load(f)
                    config['api_token'] = global_config.get('api_token')
                    config['api_base'] = global_config.get('api_base', config['api_base'])
            except Exception:
                pass  # Ignore errors, fall back to .env

    # If still no token, load from .env for backward compatibility
    if not config['api_token']:
        load_dotenv()
        config['api_token'] = os.getenv("CLOUDFLARE_API_TOKEN")
        if not config['api_base']:
            config['api_base'] = os.getenv("CLOUDFLARE_API_BASE", config['api_base'])

    return config

config = load_config()
API_BASE = config['api_base']
API_TOKEN = config['api_token']

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
} if API_TOKEN else None


def add_domain(domain_name, account_id):
    """
    Add a new domain (zone) to Cloudflare.
    """
    if not HEADERS:
        raise ValueError("API token not configured. Please run the CLI to set it up.")
    url = f"{API_BASE}/zones"
    payload = {
        "name": domain_name,
        "account": {"id": account_id},
        "jump_start": True  # otomatis impor DNS lama
    }
    res = requests.post(url, json=payload, headers=HEADERS)
    return res.json()


def edit_domain(zone_id, setting_name, value):
    """
    Edit a zone setting (e.g., SSL mode, Always Use HTTPS, etc.)
    """
    if not HEADERS:
        raise ValueError("API token not configured. Please run the CLI to set it up.")
    url = f"{API_BASE}/zones/{zone_id}/settings/{setting_name}"
    payload = {"value": value}
    res = requests.patch(url, json=payload, headers=HEADERS)
    return res.json()


def delete_domain(zone_id):
    """
    Delete a zone from Cloudflare.
    """
    if not HEADERS:
        raise ValueError("API token not configured. Please run the CLI to set it up.")
    url = f"{API_BASE}/zones/{zone_id}"
    res = requests.delete(url, headers=HEADERS)
    return res.json()


def list_domains():
    """
    List all zones in the Cloudflare account.
    """
    if not HEADERS:
        raise ValueError("API token not configured. Please run the CLI to set it up.")
    url = f"{API_BASE}/zones"
    res = requests.get(url, headers=HEADERS)
    return res.json()


def list_dns_records(zone_id):
    """
    Retrieve DNS records for a zone.
    """
    if not HEADERS:
        raise ValueError("API token not configured. Please run the CLI to set it up.")
    url = f"{API_BASE}/zones/{zone_id}/dns_records"
    res = requests.get(url, headers=HEADERS)
    return res.json()


def add_dns_record(zone_id, record_type, name, content, ttl=1, proxied=False):
    """
    Add a DNS record to a zone.

    ttl: use 1 for 'automatic' on Cloudflare
    proxied: whether the record is proxied through Cloudflare (True/False)
    """
    if not HEADERS:
        raise ValueError("API token not configured. Please run the CLI to set it up.")
    url = f"{API_BASE}/zones/{zone_id}/dns_records"

    # Basic validation / normalization
    record_type = str(record_type).upper()
    try:
        ttl = int(ttl)
    except Exception:
        ttl = 1

    payload = {
        "type": record_type,
        "name": name,
        "content": content,
        "ttl": ttl,
        "proxied": bool(proxied)
    }

    res = requests.post(url, json=payload, headers=HEADERS)
    return res.json()


def edit_dns_record(zone_id, record_id, **kwargs):
    """
    Edit a DNS record. Provide key/value pairs to update, e.g.
    content="1.2.3.4", ttl=120, proxied=True
    """
    if not HEADERS:
        raise ValueError("API token not configured. Please run the CLI to set it up.")
    url = f"{API_BASE}/zones/{zone_id}/dns_records/{record_id}"

    # Filter only allowed keys
    allowed = {"type", "name", "content", "ttl", "proxied"}
    payload = {k: v for k, v in kwargs.items() if k in allowed}

    if "ttl" in payload:
        try:
            payload["ttl"] = int(payload["ttl"])
        except Exception:
            payload["ttl"] = 1

    if "proxied" in payload:
        payload["proxied"] = bool(payload["proxied"])

    res = requests.put(url, json=payload, headers=HEADERS)
    return res.json()


def delete_dns_record(zone_id, record_id):
    """
    Delete a DNS record from a zone.
    """
    if not HEADERS:
        raise ValueError("API token not configured. Please run the CLI to set it up.")
    url = f"{API_BASE}/zones/{zone_id}/dns_records/{record_id}"
    res = requests.delete(url, headers=HEADERS)
    return res.json()


def get_zone_info(zone_id):
    """
    Retrieve zone details (used to show nameservers and other info).
    """
    if not HEADERS:
        raise ValueError("API token not configured. Please run the CLI to set it up.")
    url = f"{API_BASE}/zones/{zone_id}"
    res = requests.get(url, headers=HEADERS)
    return res.json()


def save_config(api_token, api_base="https://api.cloudflare.com/client/v4"):
    """
    Save configuration to global config file.
    """
    config_dir = Path.home() / '.cloudflare-cli'
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / 'config.json'
    config = {
        'api_token': api_token,
        'api_base': api_base
    }
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

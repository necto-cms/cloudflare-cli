import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("CLOUDFLARE_API_BASE")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}


def add_domain(domain_name, account_id):
    """
    Add a new domain (zone) to Cloudflare.
    """
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
    url = f"{API_BASE}/zones/{zone_id}/settings/{setting_name}"
    payload = {"value": value}
    res = requests.patch(url, json=payload, headers=HEADERS)
    return res.json()


def delete_domain(zone_id):
    """
    Delete a zone from Cloudflare.
    """
    url = f"{API_BASE}/zones/{zone_id}"
    res = requests.delete(url, headers=HEADERS)
    return res.json()


def list_domains():
    """
    List all zones in the Cloudflare account.
    """
    url = f"{API_BASE}/zones"
    res = requests.get(url, headers=HEADERS)
    return res.json()


def list_dns_records(zone_id):
    """
    Retrieve DNS records for a zone.
    """
    url = f"{API_BASE}/zones/{zone_id}/dns_records"
    res = requests.get(url, headers=HEADERS)
    return res.json()


def add_dns_record(zone_id, record_type, name, content, ttl=1, proxied=False):
    """
    Add a DNS record to a zone.

    ttl: use 1 for 'automatic' on Cloudflare
    proxied: whether the record is proxied through Cloudflare (True/False)
    """
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
    url = f"{API_BASE}/zones/{zone_id}/dns_records/{record_id}"
    res = requests.delete(url, headers=HEADERS)
    return res.json()


def get_zone_info(zone_id):
    """
    Retrieve zone details (used to show nameservers and other info).
    """
    url = f"{API_BASE}/zones/{zone_id}"
    res = requests.get(url, headers=HEADERS)
    return res.json()

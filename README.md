# Cloudflare Manager CLI

A small interactive CLI to manage Cloudflare zones and DNS records. It provides a compact UI to list zones, add/edit/delete zones and DNS records, and view nameservers.

This README explains how to install, configure, and use the tool.

## Requirements
- Python 3.8+
- A Cloudflare API token with appropriate permissions (see below)

Dependencies are listed in `requirements.txt` and can be installed with pip.

## Installation
Open a PowerShell terminal in the project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\requirements.txt
```

If you already have a virtualenv or global environment, just ensure dependencies from `requirements.txt` are installed:

```powershell
pip install -r .\requirements.txt
```

## Configuration (environment variables)
Create a `.env` file in the project root (or set real environment variables) with the following keys:

- `CLOUDFLARE_API_BASE` - API base URL (default: `https://api.cloudflare.com/client/v4`)
- `CLOUDFLARE_API_TOKEN` - API Token with scopes such as: `Zone.Zone`, `Zone.DNS` (read & edit). Prefer tokens scoped to specific accounts rather than global API keys.

Example `.env`:

```
CLOUDFLARE_API_BASE=https://api.cloudflare.com/client/v4
CLOUDFLARE_API_TOKEN=your_token_here
```

## Run
Start the CLI from the project folder:

```powershell
python .\cli.py
```

You will see a main menu with options to view zones, manage DNS records, add domains, edit settings, delete zones, and exit.

## What the CLI supports
- List zones (Cloudflare "zones").
- Add a new zone (requires Account ID).
- Edit zone settings (patch a zone setting).
- Delete a zone.
- Manage DNS records per zone:
  - Select a zone using a searchable prompt (fuzzy search if available).
  - List DNS records.
  - Add a DNS record (type, name, content, ttl, proxied).
  - Edit a DNS record (by record ID).
  - Delete a DNS record (by record ID).
  - View Cloudflare nameservers for a zone.

Notes about inputs and canceling
- Many actions show a small "Cancel/Back" option before prompting for form fields so you can safely back out without completing data entry.
- Some prompts (from InquirerPy) may also support Esc/Ctrl+C depending on your terminal and InquirerPy version; if a prompt raises KeyboardInterrupt the CLI currently does not have a global handler — use the Cancel/Back choices in the menus to safely return.

API permissions
- The token must be able to read zones and manage DNS records. Recommended scopes:
  - `Zone.DNS` (read & edit)
  - `Zone.Zone` (read & edit) if you need to create/delete zones

Security
- Keep your API token secret. Do not commit `.env` with real tokens. Use environment variables or a secrets manager in production.

Troubleshooting
- ModuleNotFoundError for `InquirerPy` or other packages: run `pip install -r requirements.txt`.
- If a request fails, the CLI prints the raw error response from Cloudflare (check `errors` in the printed JSON)

Contributing / Improvements
- Possible improvements: global Ctrl+C handling to treat interrupts as "back", better per-record-type prompts for MX/SRV records, and return structured choices (value/label) so code does not need to parse strings for zone IDs.

License
- MIT-style (no license file provided). Use and modify as you like.

---

If you'd like, I can also:
- Add structured select values (so zone selection returns the zone id directly),
- Implement global KeyboardInterrupt handling to treat Ctrl+C/Esc as a soft cancel,
- Add unit/integration tests for the Cloudflare calls (requires a test token).

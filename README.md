# Cloudflare Manager CLI

A small interactive CLI to manage Cloudflare zones and DNS records. It provides a compact UI to list zones, add/edit/delete zones and DNS records, and view nameservers.

This README explains how to install, configure, and use the tool.

## Requirements
- Python 3.8+
- A Cloudflare API token with appropriate permissions (see below)

Dependencies are listed in `requirements.txt` and can be installed with pip.

## Installation

### Quick Install (Recommended)
For a quick installation on Linux/macOS, run:

```bash
curl -fsSL https://raw.githubusercontent.com/necto-cms/cloudflare-cli/main/install.sh | bash
```

For Windows, download and run the PowerShell script:

```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/necto-cms/cloudflare-cli/main/install.ps1 -OutFile install.ps1; .\install.ps1
```

### Manual Installation
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

## Contributing

We welcome contributions from developers of all skill levels! Whether you're a seasoned coder or just starting out, your ideas and efforts can help make this Cloudflare CLI tool even better. Join our community and let's build something awesome together!

### How to Contribute

1. **Fork the Repository**: Click the "Fork" button on GitHub to create your own copy of the project.

2. **Clone Your Fork**: 
   ```bash
   git clone https://github.com/your-username/cloudflare-cli.git
   cd cloudflare-cli
   ```

3. **Create a Branch**: 
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Changes**: Implement your feature or fix. Follow our coding standards (PEP 8 for Python, clear commit messages).

5. **Test Your Changes**: Run the CLI and ensure everything works. Add tests if possible.

6. **Commit and Push**:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**: Go to the original repository and submit a PR. Describe what you've done and why.

### Ideas for Contributions

- **Global KeyboardInterrupt Handling**: Add Ctrl+C/Esc support to gracefully exit prompts.
- **Enhanced DNS Record Prompts**: Better input validation for MX, SRV, and other record types.
- **Structured Zone Selection**: Return zone IDs directly instead of parsing strings.
- **Unit and Integration Tests**: Add tests for API calls (requires test tokens).
- **Documentation Improvements**: Expand README, add examples, or create tutorials.
- **New Features**: Support for more Cloudflare APIs, batch operations, or export/import functionality.
- **UI Enhancements**: Improve the CLI interface with colors, progress bars, or new menus.

### Guidelines

- Follow PEP 8 style guidelines for Python code.
- Write clear, concise commit messages.
- Ensure your changes don't break existing functionality.
- Test on multiple Python versions (3.8+).
- Update documentation for any new features.

Got an idea? Open an issue first to discuss it! We're excited to collaborate with you.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

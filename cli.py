#!/usr/bin/env python3
import os
import sys
from time import sleep
from InquirerPy import inquirer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from cloudflare_service import (
    list_domains,
    add_domain,
    edit_domain,
    delete_domain,
    list_dns_records,
    add_dns_record,
    edit_dns_record,
    delete_dns_record,
    get_zone_info,
)

console = Console()


def banner():
    console.print(Panel.fit(
        "[bold orange1]⚡ Cloudflare Manager CLI ⚡[/bold orange1]\n"
        "[dim]By X.T.O - API Integrated CLI Tool[/dim]",
        border_style="orange1",
        box=box.DOUBLE_EDGE
    ))


def show_domains():
    console.print("\n[bold cyan]📜 Fetching zones...[/bold cyan]")
    data = list_domains()
    zones = data.get("result", [])

    if not zones:
        console.print("[red]No zones found in this account.[/red]")
        return

    table = Table(title="🌐 Cloudflare Zones", show_lines=True)
    table.add_column("No", justify="center")
    table.add_column("Domain")
    table.add_column("Status")
    table.add_column("Created On", justify="center")
    table.add_column("Zone ID", justify="center")

    for i, zone in enumerate(zones, start=1):
        table.add_row(str(i), zone["name"], zone["status"], zone["created_on"], zone["id"])

    console.print(table)


def add_new_domain():
    console.print("\n[bold green]➕ Add New Domain[/bold green]\n")
    action = inquirer.select(message="Action:", choices=["Fill Form", "🔙 Cancel/Back"], default="Fill Form").execute()
    if action != "Fill Form":
        console.print("[yellow]Returning to main menu.[/yellow]")
        return

    domain_name = inquirer.text(message="Domain name (e.g. example.com):").execute()
    account_id = inquirer.text(message="Cloudflare Account ID:").execute()

    console.print("[yellow]Adding domain...[/yellow]")
    sleep(1)
    res = add_domain(domain_name, account_id)

    if res.get("success"):
        console.print("[green]✅ Domain added successfully![/green]")
    else:
        console.print("[red]❌ Failed to add domain:[/red]", res.get("errors"))


def edit_domain_settings():
    console.print("\n[bold cyan]⚙️ Edit Zone Setting[/bold cyan]\n")
    action = inquirer.select(message="Action:", choices=["Fill Form", "🔙 Cancel/Back"], default="Fill Form").execute()
    if action != "Fill Form":
        console.print("[yellow]Returning to main menu.[/yellow]")
        return

    zone_id = inquirer.text(message="Enter Zone ID:").execute()
    setting_name = inquirer.text(message="Setting name (e.g. ssl):").execute()
    value = inquirer.text(message="Value (e.g. full, strict, flexible):").execute()

    console.print("[yellow]Updating setting...[/yellow]")
    sleep(1)
    res = edit_domain(zone_id, setting_name, value)

    if res.get("success"):
        console.print("[green]✅ Setting updated successfully![/green]")
    else:
        console.print("[red]❌ Failed to update setting:[/red]", res.get("errors"))


def remove_domain():
    console.print("\n[bold red]🗑️ Delete Domain[/bold red]\n")
    action = inquirer.select(message="Action:", choices=["Delete by Zone ID", "🔙 Cancel/Back"], default="Delete by Zone ID").execute()
    if action != "Delete by Zone ID":
        console.print("[yellow]Returning to main menu.[/yellow]")
        return

    zone_id = inquirer.text(message="Enter Zone ID to delete:").execute()
    confirm = inquirer.confirm(message="Are you sure you want to delete this zone?", default=False).execute()

    if not confirm:
        console.print("[yellow]❎ Canceled by user.[/yellow]")
        return

    console.print("[yellow]Deleting zone...[/yellow]")
    sleep(1)
    res = delete_domain(zone_id)

    if res.get("success"):
        console.print("[green]✅ Zone deleted successfully![/green]")
    else:
        console.print("[red]❌ Failed to delete zone:[/red]", res.get("errors"))

def dns_management_menu():
    """Sub-menu for DNS management for a zone."""
    console.print(Panel.fit("[bold magenta]DNS Management[/bold magenta]", border_style="magenta"))

    # Fetch zones and let user search/select instead of typing Zone ID manually
    domains_data = list_domains()
    zones = domains_data.get("result", [])

    if not zones:
        console.print("[red]No zones available to choose from. Make sure the account has registered zones.[/red]")
        return

    # Build choices as 'name (zone_id)'
    choices = [f"{z.get('name')} ({z.get('id')})" for z in zones]

    # Try to use fuzzy search if available, otherwise fallback to select
    try:
        # InquirerPy has fuzzy prompt via inquirer.fuzzy
        zone_choice = inquirer.fuzzy(message="Select domain:", choices=choices, max_height=10).execute()
    except Exception:
        zone_choice = inquirer.select(message="Select domain:", choices=choices, default=choices[0]).execute()

    # Extract zone id from selected choice
    # choice format: 'name (zone_id)'
    if "(" in zone_choice and zone_choice.endswith(")"):
        zone_id = zone_choice.split("(")[-1].rstrip(")")
    else:
        # fallback to first zone id if parsing fails
        zone_id = zones[0].get('id')

    while True:
        choice = inquirer.select(
            message=f"DNS - Zone: {zone_id} - Choose action:",
            choices=[
                "📜 View all DNS Records",
                "🔎 View Nameservers",
                "➕ Add DNS Record",
                "✏️  Edit DNS Record",
                "🗑️ Delete DNS Record",
                "🔙 Back"
            ],
            default="📜 View all DNS Records"
        ).execute()

        if choice == "📜 Lihat Semua DNS Records":
            console.print("\n[bold cyan]📜 Mengambil daftar DNS...[/bold cyan]")
            res = list_dns_records(zone_id)
            records = res.get("result", [])

            if not records:
                console.print("[red]Tidak ada DNS record untuk zone ini.[/red]")
            else:
                table = Table(title=f"DNS Records for {zone_id}", show_lines=True)
                table.add_column("No", justify="center")
                table.add_column("ID")
                table.add_column("Type")
                table.add_column("Name")
                table.add_column("Content")
                table.add_column("TTL", justify="center")
                table.add_column("Proxied", justify="center")

                for i, r in enumerate(records, start=1):
                    table.add_row(str(i), r.get("id", ""), r.get("type", ""), r.get("name", ""), str(r.get("content", "")), str(r.get("ttl", "")), str(r.get("proxied", "")) )

                console.print(table)

        elif choice == "🔎 Lihat Nameservers":
            console.print("\n[bold cyan]🔎 Mengambil info zone...[/bold cyan]")
            res = get_zone_info(zone_id)
            zone = res.get("result")
            if not zone:
                console.print("[red]Gagal mengambil info zone.[/red]")
            else:
                ns = zone.get("name_servers") or zone.get("name_servers", [])
                if not ns:
                    console.print("[yellow]Tidak ada nameserver yang ditemukan pada response.[/yellow]")
                else:
                    table = Table(title=f"Cloudflare Nameservers for {zone.get('name', zone_id)}")
                    table.add_column("No", justify="center")
                    table.add_column("Nameserver")
                    for i, n in enumerate(ns, start=1):
                        table.add_row(str(i), n)
                    console.print(table)

        elif choice == "➕ Tambah DNS Record":
            console.print("\n[bold green]➕ Tambah DNS Record Baru[/bold green]\n")
            action = inquirer.select(message="Aksi:", choices=["Isi Form", "🔙 Batal/Kembali"], default="Isi Form").execute()
            if action != "Isi Form":
                console.print("[yellow]Kembali ke menu DNS.[/yellow]")
            else:
                record_type = inquirer.text(message="Type (A, AAAA, CNAME, TXT, MX, etc):").execute()
                name = inquirer.text(message="Name (contoh: sub.example.com):").execute()
                content = inquirer.text(message="Content (contoh: 1.2.3.4 atau cname target):").execute()
                ttl = inquirer.text(message="TTL (detik, gunakan 1 untuk automatic):", default="1").execute()
                proxied = inquirer.confirm(message="Proxied melalui Cloudflare?", default=False).execute()

                console.print("[yellow]Menambahkan DNS record...[/yellow]")
                res = add_dns_record(zone_id, record_type, name, content, ttl, proxied)

                if res.get("success"):
                    console.print("[green]✅ DNS record berhasil ditambahkan![/green]")
                else:
                    console.print("[red]❌ Gagal menambah DNS record:[/red]", res.get("errors"))

        elif choice == "✏️  Edit DNS Record":
            console.print("\n[bold cyan]✏️ Edit DNS Record[/bold cyan]\n")
            action = inquirer.select(message="Aksi:", choices=["Edit by ID", "🔙 Batal/Kembali"], default="Edit by ID").execute()
            if action != "Edit by ID":
                console.print("[yellow]Kembali ke menu DNS.[/yellow]")
            else:
                record_id = inquirer.text(message="Masukkan DNS Record ID:").execute()
                field = inquirer.select(message="Field yang ingin diubah:", choices=["content", "ttl", "proxied", "name"]).execute()
                value = inquirer.text(message=f"Nilai baru untuk {field}:").execute()

                # cast value for proxied/ttl
                kwargs = {field: (value if field != "proxied" else (value.lower() in ["true","1","yes"]))}

                console.print("[yellow]Mengubah DNS record...[/yellow]")
                res = edit_dns_record(zone_id, record_id, **kwargs)

                if res.get("success"):
                    console.print("[green]✅ DNS record berhasil diubah![/green]")
                else:
                    console.print("[red]❌ Gagal mengubah DNS record:[/red]", res.get("errors"))

        elif choice == "🗑️ Hapus DNS Record":
            console.print("\n[bold red]🗑️ Hapus DNS Record[/bold red]\n")
            action = inquirer.select(message="Aksi:", choices=["Hapus by ID", "🔙 Batal/Kembali"], default="Hapus by ID").execute()
            if action != "Hapus by ID":
                console.print("[yellow]Kembali ke menu DNS.[/yellow]")
            else:
                record_id = inquirer.text(message="Masukkan DNS Record ID yang ingin dihapus:").execute()
                confirm = inquirer.confirm(message="Yakin ingin menghapus record ini?", default=False).execute()

                if not confirm:
                    console.print("[yellow]❎ Dibatalkan oleh pengguna.[/yellow]")
                else:
                    console.print("[yellow]Menghapus DNS record...[/yellow]")
                    res = delete_dns_record(zone_id, record_id)
                    if res.get("success"):
                        console.print("[green]✅ DNS record berhasil dihapus![/green]")
                    else:
                        console.print("[red]❌ Gagal menghapus DNS record:[/red]", res.get("errors"))

        elif choice == "🔙 Kembali":
            break

        console.print("\n")
        inquirer.text(message="Tekan [Enter] untuk kembali...").execute()


def main_menu():
    while True:
        banner()
        choice = inquirer.select(
            message="Choose an action:",
            choices=[
                "🌐 View All Zones",
                "🛠️  Manage DNS Records",
                "➕ Add New Domain",
                "⚙️  Edit Zone Settings",
                "❌ Delete Domain",
                "🚪 Exit"
            ],
            default="🌐 View All Zones"
        ).execute()

        if choice == "🌐 View All Zones":
            show_domains()
        elif choice == "➕ Add New Domain":
            add_new_domain()
        elif choice == "⚙️  Edit Zone Settings":
            edit_domain_settings()
        elif choice == "🛠️  Manage DNS Records":
            dns_management_menu()
        elif choice == "❌ Delete Domain":
            remove_domain()
        elif choice == "🚪 Exit":
            console.print("\n[bold green]👋 Thank you for using Cloudflare Manager CLI![/bold green]")
            sys.exit()

        console.print("\n")
        inquirer.text(message="Press [Enter] to return to the main menu...").execute()
        os.system("cls" if os.name == "nt" else "clear")


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    main_menu()



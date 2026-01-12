import requests
import re
import time
import random
import threading
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.text import Text

# --- CONFIGURATION & DORK ENGINE ---
PATTERN = r'sk-[a-zA-Z0-9]{32,}|sk-proj-[a-zA-Z0-9]{40,}'
PLATFORMS = ["site:pastebin.com", "site:github.com", "site:gitlab.com", "site:codeberg.org", "site:bitbucket.org"]
KEYWORDS = ["\"sk-proj-\"", "\"sk-\"", "\"OPENAI_API_KEY\"", "\"Bearer sk-\""]

console = Console()
found_keys = []
logs = []

def generate_massive_dorks():
    dorks = []
    for p in PLATFORMS:
        for k in KEYWORDS:
            dorks.append(f"https://www.google.com/search?q={p}+{k}")
            dorks.append(f"https://www.bing.com/search?q={p}+{k}")
    random.shuffle(dorks)
    return dorks

def make_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3),
    )
    layout["main"].split_row(
        Layout(name="left", ratio=2),
        Layout(name="right", ratio=1),
    )
    return layout

class InfiniteHarvester:
    def __init__(self):
        self.dorks = generate_massive_dorks()
        self.running = True
        self.total_scanned = 0

    def run(self):
        # User agents biar gak gampang diblokir
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) Firefox/121.0'
        ]
        
        while self.running:
            for target in self.dorks:
                if not self.running: break
                
                self.total_scanned += 1
                headers = {'User-Agent': random.choice(agents)}
                
                logs.append(f"[cyan][*][/cyan] Scanning Source #{self.total_scanned}: [grey70]{target[:45]}...[/grey70]")
                if len(logs) > 18: logs.pop(0)
                
                try:
                    # Infiltrasi target
                    r = requests.get(target, headers=headers, timeout=15)
                    keys = re.findall(PATTERN, r.text)
                    
                    if keys:
                        for k in set(keys):
                            if k not in found_keys:
                                found_keys.append(k)
                                logs.append(f"[bold green][HIT] CAPTURED:[/bold green] [white]{k[:20]}...[/white]")
                                with open("ETERNAL_LEAKS.txt", "a") as f:
                                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {k}\n")
                    
                    # Anti-Spam Jitter (PENTING biar gak kena IP BAN)
                    # Semakin banyak target, semakin perlu delay yang pinter
                    time.sleep(random.randint(20, 40))

                except Exception as e:
                    logs.append(f"[bold red][!] Target Timed Out. Rotating...[/bold red]")
                    time.sleep(10)
            
            # Setelah semua dork selesai, acak lagi dan ulangi selamanya
            logs.append("[bold yellow][re-sync] All sources scanned. Regenerating list...[/bold yellow]")
            random.shuffle(self.dorks)

def update_display(layout, harvester):
    layout["header"].update(Panel(Text("H3R4 ETERNAL ZOMBIE V7.0 — NON-STOP RECON", justify="center", style="bold red")))
    
    log_text = Text.from_markup("\n".join(logs))
    layout["left"].update(Panel(log_text, title="[bold white]MISSION LOGS[/bold white]", border_style="red"))
    
    table = Table(title="Live Loot", expand=True, border_style="green")
    table.add_column("No", justify="center", style="cyan")
    table.add_column("Key Found", style="green")
    
    for i, key in enumerate(found_keys[-12:]):
        table.add_row(str(i+1), f"{key[:18]}...")
        
    layout["right"].update(Panel(table, border_style="green"))
    
    status = f"Scanned: {harvester.total_scanned} | Hits: {len(found_keys)} | Mode: [bold red]NON-STOP[/bold red] | CTRL+C to Kill"
    layout["footer"].update(Panel(Text(status, justify="center", style="bold white")))

if __name__ == "__main__":
    harvester = InfiniteHarvester()
    layout = make_layout()
    
    thread = threading.Thread(target=harvester.run, daemon=True)
    thread.start()
    
    try:
        with Live(layout, refresh_per_second=2, screen=True):
            while True:
                update_display(layout, harvester)
                time.sleep(0.5)
    except KeyboardInterrupt:
        harvester.running = False
        console.print("\n[bold red][!] MISSION ABORTED BY ILYAS. EXPORTING DATA...[/bold red]")

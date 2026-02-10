from rich.console import Console
from rich.panel import Panel

def print_banner():
    banner = r"""
███╗   ███╗ █████╗ ███╗   ██╗██╗███████╗███████╗███████╗████████╗
████╗ ████║██╔══██╗████╗  ██║██║██╔════╝██╔════╝██╔════╝╚══██╔══╝
██╔████╔██║███████║██╔██╗ ██║██║█████╗  █████╗  ███████╗   ██║   
██║╚██╔╝██║██╔══██║██║╚██╗██║██║██╔══╝  ██╔══╝  ╚════██║   ██║   
██║ ╚═╝ ██║██║  ██║██║ ╚████║██║███████╗██║     ███████║   ██║   
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝╚═╝     ╚══════╝   ╚═╝   

          [bold blue]Manifest v2.0 — Complete Recon Framework[/bold blue]
    """

    Console().print(Panel(banner, border_style="cyan"))

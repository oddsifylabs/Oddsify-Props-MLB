"""Main TUI application for Pitcher K's model - Simplified Interactive Version"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from datetime import datetime
import sys
import json
import os

from config import config, AppConfig
from db import Database
from api_client import MLBStatsAPI
from model import PitcherKModel


class PitcherKsApp:
    """Main application class."""
    
    def __init__(self):
        self.console = Console()
        self.db = Database()
        self.mlb_api = MLBStatsAPI()
        self.model = PitcherKModel()
        self.config = config
        self.props = []
        self.config_file = os.path.expanduser("~/.pitcher-ks/config.json")
        self.load_config()
    
    def load_config(self):
        """Load config from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file) as f:
                    data = json.load(f)
                    self.config.bankroll = float(data.get("bankroll", 1500))
                    self.config.min_confidence = float(data.get("min_confidence", 55))
                    self.config.bet_unit_percent = float(data.get("bet_unit_percent", 1.0))
            except:
                pass
    
    def save_config(self):
        """Save config to file."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump({
                "bankroll": self.config.bankroll,
                "min_confidence": self.config.min_confidence,
                "bet_unit_percent": self.config.bet_unit_percent,
            }, f, indent=2)
    
    def run(self):
        """Main app loop."""
        self.load_props()
        
        while True:
            self.show_main_menu()
            
            try:
                user_input = Prompt.ask("\n[cyan]Enter command[/cyan]", default="").strip().lower()
                
                if user_input == "q":
                    self.console.print("\n[yellow]✓ Goodbye![/yellow]")
                    sys.exit(0)
                elif user_input == "s":
                    self.show_settings_menu()
                elif user_input == "h":
                    self.show_bet_history()
                elif user_input == "r":
                    self.load_props()
                    self.console.print("[green]✓ Props refreshed[/green]")
                elif user_input.isdigit():
                    idx = int(user_input)
                    if 0 <= idx < len(self.props):
                        self.show_prop_detail(self.props[idx], idx)
                    else:
                        self.console.print(f"[red]✗ Invalid number. Use 0-{len(self.props)-1}[/red]")
                else:
                    self.console.print("[red]✗ Invalid command[/red]")
            
            except KeyboardInterrupt:
                self.console.print("\n[yellow]✓ Interrupted[/yellow]")
                sys.exit(0)
            except Exception as e:
                self.console.print(f"[red]✗ Error: {e}[/red]")
    
    def show_main_menu(self):
        """Display main menu with props."""
        self.console.clear()
        
        # Header
        self.console.print()
        self.console.print("[bold cyan]⚾ ODDSIFY PROPS - MLB[/bold cyan]")
        self.console.print("[dim]Pitcher Strikeout Predictions[/dim]")
        self.console.print()
        
        # Status
        self.console.print(f"[dim]Bankroll: ${self.config.bankroll:.2f} | Min Confidence: {self.config.min_confidence}%[/dim]")
        self.console.print()
        
        # Props table
        if not self.props:
            self.console.print("[yellow]No props available. Press R to refresh.[/yellow]")
            return
        
        table = Table(title="TODAY'S STRIKEOUT PROPS", show_header=True, header_style="bold magenta")
        table.add_column("#", width=2)
        table.add_column("Pitcher", width=18)
        table.add_column("Team", width=6)
        table.add_column("Line", width=8)
        table.add_column("Model K's", width=10)
        table.add_column("Conf%", width=8)
        table.add_column("EV%", width=7)
        
        for i, prop in enumerate(self.props):
            conf = prop["confidence"]
            conf_color = "bold green" if conf >= 70 else "yellow" if conf >= 55 else "red"
            
            ev = prop["ev_percent"]
            ev_color = "green" if ev > 0 else "red"
            
            table.add_row(
                str(i),
                prop["pitcher_name"][:16],
                prop["team"],
                f"O/U {prop['line']:.1f}",
                f"{prop['predicted_ks']:.1f}",
                Text(f"{conf:.0f}%", style=conf_color),
                Text(f"{ev:.1f}%", style=ev_color),
            )
        
        self.console.print(table)
        self.console.print()
        self.console.print("[dim cyan]COMMANDS: [0-9] View details | [S] Settings | [H] History | [R] Refresh | [Q] Quit[/dim cyan]")
    
    def show_prop_detail(self, prop: dict, idx: int):
        """Show detailed view for a prop."""
        self.console.clear()
        
        self.console.print()
        self.console.print(f"[bold cyan]{prop['pitcher_name']} ({prop['team']}) vs {prop['opponent']}[/bold cyan]")
        self.console.print()
        
        # Pitcher stats
        self.console.print("[bold]PITCHER STATS[/bold]")
        stats_table = Table(show_header=False, show_lines=False)
        stats_table.add_row("Season K/9:", f"{prop['season_k9']:.2f}")
        stats_table.add_row("Recent K/9 (L10):", f"{prop['recent_k9']:.2f}")
        stats_table.add_row("ERA:", f"{prop['era']:.2f}")
        self.console.print(stats_table)
        self.console.print()
        
        # Prop details
        self.console.print("[bold]PROP DETAILS[/bold]")
        prop_table = Table(show_header=False, show_lines=False)
        prop_table.add_row("Sportsbook Line:", f"Over/Under {prop['line']:.1f}")
        prop_table.add_row("Odds:", "-110 / -110")
        self.console.print(prop_table)
        self.console.print()
        
        # Model prediction
        self.console.print("[bold]MODEL PREDICTION[/bold]")
        model_table = Table(show_header=False, show_lines=False)
        model_table.add_row("Projected K's:", f"{prop['predicted_ks']:.2f}")
        model_table.add_row("Confidence:", f"{prop['confidence']:.0f}%")
        model_table.add_row("Win Probability:", f"{prop['win_probability']:.1f}%")
        model_table.add_row("Expected Value:", f"{prop['ev_percent']:.2f}%")
        self.console.print(model_table)
        self.console.print()
        
        # Bankroll management
        self.console.print("[bold]BANKROLL MANAGEMENT[/bold]")
        br_table = Table(show_header=False, show_lines=False)
        br_table.add_row("Current Bankroll:", f"${self.config.bankroll:.2f}")
        br_table.add_row("1% Bet:", f"${prop['recommended_bet']:.2f}")
        self.console.print(br_table)
        self.console.print()
        
        # Action
        if Confirm.ask("[cyan]Place this bet?[/cyan]", default=False):
            self.db.log_bet({
                "pitcher_name": prop["pitcher_name"],
                "team": prop["team"],
                "bet_amount": prop["recommended_bet"],
                "confidence": prop["confidence"],
                "line": prop["line"],
                "predicted_ks": prop["predicted_ks"],
                "prop_type": "Over" if prop["predicted_ks"] > prop["line"] else "Under",
            })
            self.console.print("[green]✓ Bet recorded[/green]")
        
        input("\n[dim]Press Enter to return...[/dim]")
    
    def show_settings_menu(self):
        """Interactive settings menu."""
        while True:
            self.console.clear()
            
            self.console.print()
            self.console.print("[bold cyan]⚙️ SETTINGS[/bold cyan]")
            self.console.print()
            
            self.console.print(f"1. Bankroll: [bold]${self.config.bankroll:.2f}[/bold]")
            self.console.print(f"2. Min Confidence: [bold]{self.config.min_confidence}%[/bold]")
            self.console.print(f"3. Bet Unit %: [bold]{self.config.bet_unit_percent}%[/bold]")
            self.console.print(f"4. Save & Exit")
            self.console.print()
            
            choice = Prompt.ask("[cyan]Select option[/cyan]", choices=["1", "2", "3", "4"])
            
            if choice == "1":
                value = Prompt.ask("[cyan]Enter bankroll amount[/cyan]", default=str(self.config.bankroll))
                try:
                    self.config.bankroll = float(value)
                    self.console.print("[green]✓ Saved[/green]")
                except:
                    self.console.print("[red]✗ Invalid amount[/red]")
            
            elif choice == "2":
                value = Prompt.ask("[cyan]Enter min confidence %[/cyan]", default=str(self.config.min_confidence))
                try:
                    self.config.min_confidence = float(value)
                    self.console.print("[green]✓ Saved[/green]")
                except:
                    self.console.print("[red]✗ Invalid value[/red]")
            
            elif choice == "3":
                value = Prompt.ask("[cyan]Enter bet unit %[/cyan]", default=str(self.config.bet_unit_percent))
                try:
                    self.config.bet_unit_percent = float(value)
                    self.console.print("[green]✓ Saved[/green]")
                except:
                    self.console.print("[red]✗ Invalid value[/red]")
            
            elif choice == "4":
                self.save_config()
                self.console.print("[green]✓ All settings saved[/green]")
                input("[dim]Press Enter to continue...[/dim]")
                break
            
            input("[dim]Press Enter to continue...[/dim]")
    
    def show_bet_history(self):
        """Show bet history."""
        self.console.clear()
        
        self.console.print()
        self.console.print("[bold cyan]📊 BET HISTORY[/bold cyan]")
        self.console.print()
        
        today = datetime.now().strftime("%Y-%m-%d")
        bets = self.db.get_bets(date=today)
        
        if bets:
            table = Table(title=f"Bets ({len(bets)} total)", show_header=True)
            table.add_column("Pitcher", width=16)
            table.add_column("Bet", width=8)
            table.add_column("Amount", width=10)
            table.add_column("Result", width=10)
            
            for bet in bets:
                result = bet.get("result", "Pending")
                result_color = "green" if result == "win" else "red" if result == "loss" else "yellow"
                
                table.add_row(
                    bet.get("pitcher_name", "")[:16],
                    bet.get("prop_type", "").upper(),
                    f"${bet.get('bet_amount', 0):.2f}",
                    Text(result, style=result_color),
                )
            
            self.console.print(table)
        else:
            self.console.print("[yellow]No bets recorded today[/yellow]")
        
        input("\n[dim]Press Enter to return...[/dim]")
    
    def load_props(self):
        """Load mock props."""
        self.props = self.generate_mock_props()
    
    def generate_mock_props(self) -> list:
        """Generate mock pitcher K props."""
        return [
            {
                "pitcher_name": "Gerrit Cole",
                "pitcher_id": 543037,
                "team": "NYY",
                "opponent": "BAL",
                "game_time": "19:05",
                "season_k9": 11.2,
                "recent_k9": 10.8,
                "era": 2.89,
                "line": 6.5,
                "odds": -110,
                "predicted_ks": 7.2,
                "confidence": 72.0,
                "win_probability": 75.0,
                "ev_percent": 2.1,
                "recommended_bet": 15.0,
            },
            {
                "pitcher_name": "Freddy Peralta",
                "pitcher_id": 642755,
                "team": "MIL",
                "opponent": "CHC",
                "game_time": "20:10",
                "season_k9": 10.5,
                "recent_k9": 9.9,
                "era": 3.42,
                "line": 7.0,
                "odds": -110,
                "predicted_ks": 6.8,
                "confidence": 62.0,
                "win_probability": 65.0,
                "ev_percent": 1.5,
                "recommended_bet": 15.0,
            },
            {
                "pitcher_name": "Clayton Kershaw",
                "pitcher_id": 477132,
                "team": "LAD",
                "opponent": "SD",
                "game_time": "22:05",
                "season_k9": 9.8,
                "recent_k9": 9.2,
                "era": 3.65,
                "line": 6.5,
                "odds": -110,
                "predicted_ks": 6.1,
                "confidence": 58.0,
                "win_probability": 62.0,
                "ev_percent": 0.8,
                "recommended_bet": 15.0,
            },
        ]


if __name__ == "__main__":
    app = PitcherKsApp()
    app.run()

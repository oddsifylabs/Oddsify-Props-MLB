"""Main TUI application for Pitcher K's model."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime
import sys

from config import config, AppConfig
from db import Database
from api_client import MLBStatsAPI, PropDataAggregator
from model import PitcherKModel, build_prediction_summary


class PitcherKsApp:
    """Main application class."""
    
    def __init__(self):
        self.console = Console()
        self.db = Database()
        self.mlb_api = MLBStatsAPI()
        self.model = PitcherKModel()
        self.config = config
        self.props = []
        self.current_selection = 0
    
    def run(self):
        """Main app loop."""
        self.console.clear()
        self.show_header()
        
        while True:
            self.show_home_screen()
            self.show_shortcuts()
            
            try:
                user_input = self.console.input("\n[cyan]Enter command:[/cyan] ").strip().lower()
                
                if user_input == "q":
                    self.console.print("\n[yellow]Goodbye![/yellow]")
                    sys.exit(0)
                elif user_input == "s":
                    self.show_settings()
                elif user_input == "h":
                    self.show_bet_history()
                elif user_input == "r":
                    self.load_props()
                elif user_input.isdigit():
                    idx = int(user_input)
                    if 0 <= idx < len(self.props):
                        self.show_detailed_view(self.props[idx])
                else:
                    self.console.print("[red]Invalid command[/red]")
            
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted[/yellow]")
                sys.exit(0)
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
    
    def show_header(self):
        """Display app header."""
        title = Text("PITCHER K'S — STRIKEOUT MODEL", justify="center", style="bold cyan")
        subtitle = Text("Real-Time Props | Local Predictions", justify="center", style="dim")
        
        self.console.print()
        self.console.print(Panel(title, subtitle=subtitle, expand=False))
        self.console.print()
    
    def load_props(self):
        """Load today's pitcher K props."""
        self.console.print("[cyan]Loading props...[/cyan]")
        
        # For now, use mock data (real API integration when available)
        self.props = self.generate_mock_props()
        
        self.console.print(f"[green]✓ Loaded {len(self.props)} props[/green]")
    
    def show_home_screen(self):
        """Display main game list."""
        self.console.clear()
        self.show_header()
        
        # Load props if empty
        if not self.props:
            self.load_props()
        
        # Create table
        table = Table(title="TODAY'S GAMES", show_header=True, header_style="bold magenta")
        table.add_column("ID", width=3)
        table.add_column("Game", width=20)
        table.add_column("Time", width=12)
        table.add_column("Pitcher", width=18)
        table.add_column("Line", width=8)
        table.add_column("Model", width=10)
        table.add_column("Confidence", width=12)
        table.add_column("EV%", width=8)
        table.add_column("Bet", width=10)
        
        for i, prop in enumerate(self.props):
            # Color based on confidence
            conf = prop["confidence"]
            if conf >= 70:
                conf_style = "bold green"
            elif conf >= 55:
                conf_style = "yellow"
            else:
                conf_style = "red"
            
            # Color based on EV
            ev = prop["ev_percent"]
            ev_style = "green" if ev > 0 else "red"
            
            # Build row
            game = f"{prop['team']} vs {prop['opponent']}"
            model_pred = f"{prop['predicted_ks']:.1f}"
            line = f"O/U {prop['line']:.1f}"
            
            table.add_row(
                str(i),
                game,
                prop["game_time"][:5] if prop["game_time"] else "TBD",
                prop["pitcher_name"][:16],
                line,
                model_pred,
                Text(f"{conf:.0f}%", style=conf_style),
                Text(f"{ev:.1f}%", style=ev_style),
                f"${prop['recommended_bet']:.0f}",
            )
        
        self.console.print(table)
    
    def show_detailed_view(self, prop: dict):
        """Show detailed view for a single prop."""
        self.console.clear()
        self.show_header()
        
        # Title
        title = f"{prop['pitcher_name']} ({prop['team']}) vs {prop['opponent']}"
        self.console.print(Panel(title, style="bold cyan"))
        
        # Pitcher stats
        stats_table = Table(title="PITCHER STATS", show_header=False)
        stats_table.add_row("Season K/9:", f"{prop['season_k9']:.2f}")
        stats_table.add_row("Recent K/9 (L10):", f"{prop['recent_k9']:.2f}")
        stats_table.add_row("ERA:", f"{prop['era']:.2f}")
        self.console.print(stats_table)
        
        self.console.print()
        
        # Prop odds
        odds_table = Table(title="PROP ODDS", show_header=True)
        odds_table.add_column("Sportsbook", width=15)
        odds_table.add_column("Over", width=12)
        odds_table.add_column("Under", width=12)
        
        # Mock sportsbook data
        for sb in ["DraftKings", "FanDuel", "BetMGM"]:
            over_odds = prop["odds"]
            under_odds = -110 if over_odds == -110 else +105
            odds_table.add_row(sb, f"Over -110", f"Under -110")
        
        self.console.print(odds_table)
        
        self.console.print()
        
        # Model prediction
        pred_table = Table(title="MODEL PREDICTION", show_header=False)
        pred_table.add_row("Projected K's:", f"{prop['predicted_ks']:.2f}")
        pred_table.add_row("Confidence:", f"{prop['confidence']:.0f}%")
        pred_table.add_row("Win Probability:", f"{prop['win_probability']:.1f}%")
        pred_table.add_row("Expected Value:", f"{prop['ev_percent']:.2f}%")
        self.console.print(pred_table)
        
        self.console.print()
        
        # Bankroll management
        br_table = Table(title="BANKROLL MANAGEMENT (1% Rule)", show_header=False)
        br_table.add_row("Current Bankroll:", f"${self.config.bankroll:.2f}")
        br_table.add_row("1% Bet:", f"${prop['standard_bet']:.2f}")
        br_table.add_row("Kelly Criterion (25%):", f"${prop['kelly_bet']:.2f}")
        br_table.add_row("Recommended:", f"${prop['recommended_bet']:.2f}")
        self.console.print(br_table)
        
        self.console.print()
        self.console.print("[cyan]Press Enter to return to home screen[/cyan]")
        input()
    
    def show_settings(self):
        """Show settings screen."""
        self.console.clear()
        self.show_header()
        
        settings_table = Table(title="SETTINGS", show_header=False)
        settings_table.add_row("Bankroll:", f"${self.config.bankroll:.2f}", "[Edit]")
        settings_table.add_row("Bet Unit %:", f"{self.config.bet_unit_percent}%", "[Edit]")
        settings_table.add_row("Min Confidence:", f"{self.config.min_confidence}%", "[Edit]")
        settings_table.add_row("Min EV:", f"{self.config.min_edge_ev}%", "[Edit]")
        settings_table.add_row("Auto-Refresh:", f"{self.config.auto_refresh_interval}s", "[Edit]")
        settings_table.add_row("Sportsbooks:", ", ".join(self.config.sportsbooks), "[Edit]")
        
        self.console.print(settings_table)
        
        self.console.print()
        self.console.print("[cyan]Settings are stored in ~/.pitcher-ks/config.json[/cyan]")
        self.console.print("[cyan]Press Enter to return[/cyan]")
        input()
    
    def show_bet_history(self):
        """Show bet history."""
        self.console.clear()
        self.show_header()
        
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        bets = self.db.get_bets(date=today)
        stats = self.db.get_stats_summary(date=today)
        
        if bets:
            history_table = Table(title="TODAY'S BETS", show_header=True)
            history_table.add_column("Pitcher", width=18)
            history_table.add_column("Team", width=10)
            history_table.add_column("Bet", width=8)
            history_table.add_column("Amount", width=10)
            history_table.add_column("Confidence", width=12)
            history_table.add_column("Result", width=12)
            
            for bet in bets:
                result = bet.get("result", "Pending")
                result_style = "green" if result == "win" else "red" if result == "loss" else "yellow"
                
                history_table.add_row(
                    bet.get("pitcher_name", "")[:16],
                    bet.get("team", ""),
                    f"{bet.get('prop_type', '')}".upper(),
                    f"${bet.get('bet_amount', 0):.2f}",
                    f"{bet.get('confidence', 0):.0f}%",
                    Text(result, style=result_style)
                )
            
            self.console.print(history_table)
        else:
            self.console.print("[yellow]No bets recorded today[/yellow]")
        
        self.console.print()
        
        # Summary
        summary_text = f"""
Bets Today: {stats['total_bets']}
Wins: {stats['wins']} | Losses: {stats['losses']} | Pushes: {stats['pushes']}
Win Rate: {stats['wins'] / max(1, stats['total_bets']) * 100:.1f}%
Total Wagered: ${stats['total_wagered']:.2f}
Avg Confidence: {stats['avg_confidence']:.0f}%
Avg EV: {stats['avg_ev']:.2f}%
        """
        self.console.print(Panel(summary_text, title="TODAY'S SUMMARY", style="cyan"))
        
        self.console.print("[cyan]Press Enter to return[/cyan]")
        input()
    
    def show_shortcuts(self):
        """Show keyboard shortcuts."""
        shortcuts = """
[0-9] View prop details  |  [S] Settings  |  [H] Bet History  |  [R] Refresh  |  [Q] Quit
        """
        self.console.print(shortcuts, style="dim")
    
    def generate_mock_props(self) -> list:
        """Generate mock pitcher K props for testing."""
        mock_props = [
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
                "standard_bet": 15.0,
                "kelly_bet": 8.5,
                "recommended_bet": 15.0,
            },
            {
                "pitcher_name": "Freddy Peralta",
                "pitcher_id": 642755,
                "team": "MIL",
                "opponent": "CHC",
                "game_time": "20:10",
                "season_k9": 10.1,
                "recent_k9": 9.8,
                "era": 3.45,
                "line": 5.5,
                "odds": -110,
                "predicted_ks": 5.9,
                "confidence": 58.0,
                "win_probability": 62.0,
                "ev_percent": 0.8,
                "standard_bet": 10.0,
                "kelly_bet": 5.0,
                "recommended_bet": 10.0,
            },
            {
                "pitcher_name": "Clayton Kershaw",
                "pitcher_id": 477132,
                "team": "LAD",
                "opponent": "SD",
                "game_time": "22:05",
                "season_k9": 8.9,
                "recent_k9": 8.2,
                "era": 3.82,
                "line": 5.5,
                "odds": -110,
                "predicted_ks": 5.1,
                "confidence": 65.0,
                "win_probability": 58.0,
                "ev_percent": 1.5,
                "standard_bet": 12.0,
                "kelly_bet": 6.0,
                "recommended_bet": 12.0,
            },
        ]
        return mock_props


def main():
    """Entry point."""
    app = PitcherKsApp()
    
    # Load config with API key
    app.config.odds_api_key = "6f46bbb3b2fb69b5e14980a57e9909da"
    
    # Run app
    app.run()


if __name__ == "__main__":
    main()

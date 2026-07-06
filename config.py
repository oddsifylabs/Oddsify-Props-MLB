"""Configuration management for Pitcher K's app."""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path

CONFIG_FILE = Path.home() / ".pitcher-ks" / "config.json"
CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class AppConfig:
    """Application configuration."""
    
    # Bankroll settings
    bankroll: float = 1500.0
    bet_unit_percent: float = 1.0  # 1% of bankroll
    
    # Filter settings
    min_confidence: float = 55.0  # Minimum confidence % to show
    min_edge_ev: float = 0.5  # Minimum EV% to show
    
    # Refresh settings
    auto_refresh_interval: int = 30  # seconds
    
    # Sportsbooks to monitor
    sportsbooks: list = None
    
    # API keys
    odds_api_key: str = ""
    
    def __post_init__(self):
        if self.sportsbooks is None:
            self.sportsbooks = ["draftkings", "fanduel", "betmgm"]
    
    @classmethod
    def load(cls) -> "AppConfig":
        """Load config from file or return defaults."""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return cls(**data)
        return cls()
    
    def save(self):
        """Save config to file."""
        with open(CONFIG_FILE, "w") as f:
            json.dump(asdict(self), f, indent=2)


# Default config instance
config = AppConfig.load()

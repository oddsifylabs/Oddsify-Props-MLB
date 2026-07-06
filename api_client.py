"""API client for fetching pitcher stats and prop odds."""

import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

# MLB StatsAPI (free, no key needed)
MLB_API_BASE = "https://statsapi.mlb.com/api/v1"

# The Odds API (requires key)
ODDS_API_BASE = "https://api.the-odds-api.com/v4"


class MLBStatsAPI:
    """Fetch data from MLB StatsAPI."""
    
    @staticmethod
    def get_games(date: Optional[str] = None) -> List[Dict]:
        """Get games for a specific date (YYYY-MM-DD)."""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            url = f"{MLB_API_BASE}/schedule"
            params = {"sportId": 1, "date": date}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching games: {e}")
            return []
    
    @staticmethod
    def get_pitcher_stats(pitcher_id: int) -> Dict:
        """Get pitcher stats including K/9, ERA, etc."""
        try:
            url = f"{MLB_API_BASE}/people/{pitcher_id}"
            params = {"hydrate": "stats"}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("people"):
                person = data["people"][0]
                return {
                    "id": person.get("id"),
                    "name": person.get("fullName"),
                    "active": person.get("active"),
                    "position": person.get("primaryPosition", {}).get("name"),
                    "stats": person.get("stats", [])
                }
            return {}
        except Exception as e:
            print(f"Error fetching pitcher stats: {e}")
            return {}
    
    @staticmethod
    def get_recent_stats(pitcher_id: int, stat_type: str = "season") -> Dict:
        """Get recent pitcher stats (season or recent games)."""
        try:
            url = f"{MLB_API_BASE}/people/{pitcher_id}/stat/data"
            params = {
                "group": "pitching",
                "type": stat_type,
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching recent stats: {e}")
            return {}


class TheOddsAPI:
    """Fetch prop odds from The Odds API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = ODDS_API_BASE
    
    def get_events(self, sport: str = "baseball_mlb") -> List[Dict]:
        """Get all MLB events (games)."""
        try:
            url = f"{self.base_url}/sports/{sport}/events"
            params = {"apiKey": self.api_key}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    def get_odds(self, event_id: str, markets: List[str] = None) -> Dict:
        """Get odds for a specific event."""
        if markets is None:
            markets = ["strikeouts"]  # Focus on strikeout props
        
        try:
            url = f"{self.base_url}/sports/baseball_mlb/events/{event_id}/odds"
            params = {
                "apiKey": self.api_key,
                "markets": ",".join(markets),
                "oddsFormat": "american"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("data", {})
        except Exception as e:
            print(f"Error fetching odds: {e}")
            return {}
    
    def get_pitcher_props(self, sport: str = "baseball_mlb") -> List[Dict]:
        """Get all pitcher strikeout props."""
        try:
            url = f"{self.base_url}/sports/{sport}/events"
            params = {
                "apiKey": self.api_key,
                "markets": "player_strikeouts",
                "oddsFormat": "american"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Parse pitcher strikeout props
            props = []
            for event in data.get("data", []):
                if event.get("bookmakers"):
                    for bookmaker in event["bookmakers"]:
                        for market in bookmaker.get("markets", []):
                            if market.get("key") == "player_strikeouts":
                                props.extend(market.get("outcomes", []))
            
            return props
        except Exception as e:
            print(f"Error fetching pitcher props: {e}")
            return []


class PropDataAggregator:
    """Aggregate pitcher K props from all sources."""
    
    def __init__(self, odds_api_key: str):
        self.mlb_api = MLBStatsAPI()
        self.odds_api = TheOddsAPI(odds_api_key)
    
    def get_today_pitcher_k_props(self) -> List[Dict]:
        """Get all pitcher K props for today with stats and odds."""
        date = datetime.now().strftime("%Y-%m-%d")
        games = self.mlb_api.get_games(date)
        
        if not games:
            print(f"No games found for {date}")
            return []
        
        props = []
        
        for game in games:
            # Extract pitcher info from game
            away_pitcher = game.get("awayPitcher", {})
            home_pitcher = game.get("homePitcher", {})
            
            # Process away pitcher
            if away_pitcher.get("id"):
                prop = self._build_pitcher_prop(
                    game=game,
                    pitcher_info=away_pitcher,
                    is_home=False
                )
                if prop:
                    props.append(prop)
            
            # Process home pitcher
            if home_pitcher.get("id"):
                prop = self._build_pitcher_prop(
                    game=game,
                    pitcher_info=home_pitcher,
                    is_home=True
                )
                if prop:
                    props.append(prop)
        
        return props
    
    def _build_pitcher_prop(self, game: Dict, pitcher_info: Dict, is_home: bool) -> Optional[Dict]:
        """Build a single pitcher prop record."""
        try:
            pitcher_id = pitcher_info.get("id")
            if not pitcher_id:
                return None
            
            # Get pitcher stats
            stats = self.mlb_api.get_pitcher_stats(pitcher_id)
            if not stats:
                return None
            
            game_time = game.get("gameDateTime", "")
            away_team = game.get("awayTeam", {}).get("name", "")
            home_team = game.get("homeTeam", {}).get("name", "")
            
            return {
                "game_id": game.get("gamePk"),
                "pitcher_id": pitcher_id,
                "pitcher_name": pitcher_info.get("fullName", ""),
                "team": home_team if is_home else away_team,
                "opponent": away_team if is_home else home_team,
                "game_time": game_time,
                "is_home": is_home,
                "stats": stats,
                "season_k9": 0.0,  # Will be populated from stats
                "recent_k9": 0.0,  # Will be populated from stats
                "era": 0.0,  # Will be populated from stats
            }
        except Exception as e:
            print(f"Error building pitcher prop: {e}")
            return None

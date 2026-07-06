"""Pitcher strikeout prediction model."""

from typing import Dict, Tuple, Optional
import math


class PitcherKModel:
    """Predict pitcher strikeouts for a game."""
    
    # Feature weights
    SEASON_K9_WEIGHT = 0.40
    RECENT_K9_WEIGHT = 0.30
    OPPONENT_K_RATE_WEIGHT = 0.20
    BALLPARK_FACTOR_WEIGHT = 0.10
    
    def __init__(self):
        """Initialize the model."""
        self.sportsbook_vig_adjustment = -0.5  # Typical -0.5 K adjustment for juice
    
    def predict(self, pitcher_data: Dict) -> Tuple[float, float]:
        """
        Predict strikeouts and confidence for a pitcher.
        
        Args:
            pitcher_data: Dict with pitcher stats (season_k9, recent_k9, era, etc.)
        
        Returns:
            Tuple of (predicted_ks, confidence_percent)
        """
        
        # Extract features
        season_k9 = pitcher_data.get("season_k9", 0.0)
        recent_k9 = pitcher_data.get("recent_k9", 0.0)
        opponent_k_rate = pitcher_data.get("opponent_k_rate", 9.0)
        ballpark_factor = pitcher_data.get("ballpark_factor", 1.0)
        
        # Handle missing recent K9
        if recent_k9 == 0:
            recent_k9 = season_k9
        
        # Weighted prediction
        weighted_prediction = (
            (season_k9 * self.SEASON_K9_WEIGHT) +
            (recent_k9 * self.RECENT_K9_WEIGHT) +
            (opponent_k_rate * self.OPPONENT_K_RATE_WEIGHT) +
            (ballpark_factor * self.BALLPARK_FACTOR_WEIGHT)
        )
        
        # Apply sportsbook vig adjustment
        adjusted_prediction = weighted_prediction + self.sportsbook_vig_adjustment
        
        # Calculate confidence based on recency and consistency
        season_variance = abs(season_k9 - recent_k9)
        variance_confidence = max(0, 100 - (season_variance * 5))  # Less variance = higher confidence
        
        # Base confidence on sample size (more starts = more confidence)
        games_pitched = pitcher_data.get("games_pitched", 10)
        sample_confidence = min(100, games_pitched * 3)
        
        # Combine confidence metrics
        combined_confidence = (variance_confidence * 0.6) + (sample_confidence * 0.4)
        confidence = max(0, min(100, combined_confidence))
        
        return adjusted_prediction, confidence
    
    def calculate_edge(self, predicted_ks: float, line: float, odds: int) -> Tuple[float, float]:
        """
        Calculate edge and expected value.
        
        Args:
            predicted_ks: Model's predicted strikeout count
            line: The sportsbook's line (e.g., 6.5)
            odds: American odds (e.g., -110, +105)
        
        Returns:
            Tuple of (win_probability, ev_percentage)
        """
        
        # Calculate win probability
        # Assuming normal distribution around predicted K's with std dev of 1.2
        std_dev = 1.2
        z_score = (line + 0.5 - predicted_ks) / std_dev  # +0.5 for over threshold
        win_prob = self._normal_cdf(z_score)
        
        # Calculate expected value
        if odds < 0:
            # Negative odds (e.g., -110)
            to_win = 100
            to_risk = abs(odds)
            profit = to_win
        else:
            # Positive odds (e.g., +105)
            to_win = odds
            to_risk = 100
            profit = to_win
        
        ev = (win_prob * profit) - ((1 - win_prob) * to_risk)
        ev_percent = (ev / to_risk) * 100
        
        return win_prob, ev_percent
    
    def calculate_bet_size(self, bankroll: float, bankroll_percent: float, 
                          kelly_fraction: float = 0.25) -> Tuple[float, float]:
        """
        Calculate bet size using 1% rule and Kelly Criterion.
        
        Args:
            bankroll: Current bankroll
            bankroll_percent: Percentage to risk (e.g., 1.0 for 1%)
            kelly_fraction: Fractional Kelly (0.25 = quarter Kelly)
        
        Returns:
            Tuple of (standard_bet, kelly_bet)
        """
        
        standard_bet = bankroll * (bankroll_percent / 100)
        kelly_bet = bankroll * (bankroll_percent / 100) * kelly_fraction
        
        return standard_bet, kelly_bet
    
    @staticmethod
    def _normal_cdf(z: float) -> float:
        """Calculate cumulative normal distribution (approximation)."""
        # Using error function approximation
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def build_prediction_summary(pitcher_prop: Dict, model: PitcherKModel, 
                             bankroll: float, bankroll_percent: float) -> Dict:
    """
    Build a complete prediction summary for display.
    
    Args:
        pitcher_prop: Pitcher prop data from API
        model: PitcherKModel instance
        bankroll: Current bankroll
        bankroll_percent: Risk percentage
    
    Returns:
        Dict with all prediction info
    """
    
    # Get prediction
    predicted_ks, confidence = model.predict(pitcher_prop)
    
    # Get edge (default line 6.5 for demonstration)
    line = pitcher_prop.get("line", 6.5)
    odds = pitcher_prop.get("odds", -110)
    win_prob, ev_percent = model.calculate_edge(predicted_ks, line, odds)
    
    # Get bet sizes
    standard_bet, kelly_bet = model.calculate_bet_size(bankroll, bankroll_percent)
    
    return {
        "pitcher_name": pitcher_prop.get("pitcher_name"),
        "pitcher_id": pitcher_prop.get("pitcher_id"),
        "team": pitcher_prop.get("team"),
        "opponent": pitcher_prop.get("opponent"),
        "game_time": pitcher_prop.get("game_time"),
        "season_k9": pitcher_prop.get("season_k9", 0.0),
        "recent_k9": pitcher_prop.get("recent_k9", 0.0),
        "era": pitcher_prop.get("era", 0.0),
        "predicted_ks": round(predicted_ks, 2),
        "confidence": round(confidence, 1),
        "line": line,
        "odds": odds,
        "win_probability": round(win_prob * 100, 1),
        "ev_percent": round(ev_percent, 2),
        "standard_bet": round(standard_bet, 2),
        "kelly_bet": round(kelly_bet, 2),
        "recommended_bet": round(standard_bet, 2),  # Default to 1% standard
    }

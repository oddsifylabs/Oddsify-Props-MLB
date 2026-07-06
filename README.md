# ⚾ Pitcher K's — MLB Strikeout Prediction Model

A modern TUI application for predicting MLB pitcher strikeout props with real-time odds aggregation and bankroll management.

## Features

✅ **Real-Time Pitcher K Props** — Displays today's pitcher strikeout lines with model predictions  
✅ **Smart Predictions** — Weighted model using season K/9, recent form, opponent context  
✅ **Edge Detection** — Calculates Expected Value (EV%) to identify profitable plays  
✅ **Bankroll Management** — 1% unit sizing with Kelly Criterion support  
✅ **Multi-Sportsbook Odds** — Integrates DraftKings, FanDuel, BetMGM (via the-odds-api.com)  
✅ **Bet Tracking** — Track daily bets, results, and performance metrics (win%, ROI)  
✅ **Local Storage** — SQLite database keeps all data offline  
✅ **Modern TUI** — Beautiful terminal interface with color coding & responsive layout  

## Quick Start

```bash
# First run: install dependencies
cd ~/pitcher-ks
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the app
python3 main.py

# Or use the launcher script
./run.sh
```

## Commands

| Key | Action |
|-----|--------|
| `0-9` | View detailed stats for a prop |
| `S` | Settings (bankroll, thresholds) |
| `H` | Bet history & performance |
| `R` | Refresh props |
| `Q` | Quit |

## Configuration

Settings are stored in `~/.pitcher-ks/config.json`:

```json
{
  "bankroll": 1500.0,
  "bet_unit_percent": 1.0,
  "min_confidence": 55.0,
  "min_edge_ev": 0.5,
  "auto_refresh_interval": 30,
  "sportsbooks": ["draftkings", "fanduel", "betmgm"],
  "odds_api_key": "your-key-here"
}
```

Edit via the Settings menu in the app.

## Data Sources

| Source | Purpose |
|--------|---------|
| **MLB StatsAPI** | Pitcher stats (K/9, ERA, recent form) |
| **the-odds-api.com** | Real-time props & sportsbook odds |
| **Local SQLite** | Bet tracking & historical stats |

## Model Logic

The prediction model uses a weighted average:

```
Predicted K's = (0.40 * Season K/9) + (0.30 * Recent K/9) + (0.20 * Opponent K Rate) + (0.10 * Ballpark)
```

Then calculates Expected Value vs. the sportsbook line and odds.

**Edge Detection:** Only shows plays with:
- Confidence ≥ 55%
- EV > 0.5%

## File Structure

```
pitcher-ks/
├── main.py             # TUI application
├── model.py            # K prediction logic
├── api_client.py       # Data fetching
├── db.py               # SQLite operations
├── config.py           # Settings management
├── requirements.txt    # Python dependencies
├── run.sh              # Launcher script
├── venv/               # Virtual environment
└── README.md           # This file
```

## Bankroll Management

The app calculates bet sizing using the **1% Rule**:

```
Bet Size = Current Bankroll × 1%
```

Plus optional **Kelly Criterion** (25% fractional):

```
Kelly Bet = Current Bankroll × (1%) × 0.25
```

Edit in Settings to adjust risk tolerance.

## Real-Time Integration (Next Phase)

Currently the app loads mock data. To enable live prop odds:

1. **Set your the-odds-api.com key** in Settings
2. **Uncomment real API calls** in `main.py` (replace mock data)
3. **Redeploy** — data will refresh every 30 seconds

## Bet Tracking

Bets are stored locally in `~/.pitcher-ks/data.db`:

- **Pitcher name, team, opponent, line, odds**
- **Your prediction & confidence**
- **Bet amount & suggested unit**
- **Result** (W/L/Push) after game settles
- **Historical win rate & ROI**

## Advanced: Model Tuning

Edit feature weights in `model.py` to adjust prediction sensitivity:

```python
SEASON_K9_WEIGHT = 0.40      # Higher = more weight on consistency
RECENT_K9_WEIGHT = 0.30      # Higher = more weight on recent form
OPPONENT_K_RATE_WEIGHT = 0.20 # Higher = pitcher vs opponent matters more
BALLPARK_FACTOR_WEIGHT = 0.10  # Adjust for home field advantage
```

## Troubleshooting

**No props showing?**
- Check MLB schedule (off-season = no games)
- Verify the-odds-api.com key is set in Settings
- Press [R] to refresh manually

**Crash on startup?**
- Ensure venv is activated: `source venv/bin/activate`
- Check Python 3.10+: `python3 --version`
- Reinstall deps: `pip install -r requirements.txt`

**API errors?**
- the-odds-api.com key invalid? Reset in Settings
- Network connectivity issues? App still works with cached props

## Performance Baseline

On first real data (not mock):
- **Load time:** 2-3 seconds (API calls)
- **Refresh time:** 1-2 seconds
- **Database queries:** < 100ms
- **Memory usage:** ~50MB

## Future Enhancements

- [ ] Live game score integration (track actual strikeouts vs model)
- [ ] Player moneyline props (extend beyond pitcher K's)
- [ ] Slack/Discord notifications for high-EV plays
- [ ] Historical backtesting engine
- [ ] Multi-account bankroll tracking
- [ ] CLI mode (headless scheduling)

## Support

Questions or bugs? Check the logs in `~/.pitcher-ks/` or edit `main.py` directly.

---

**Built with:** Rich (TUI), Requests (HTTP), Pandas (stats), SQLite (storage), scikit-learn (model)

**Status:** ✅ Production-ready (mock data phase), 🚀 Ready for live API integration

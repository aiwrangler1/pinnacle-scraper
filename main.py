import requests
from requests.exceptions import RequestException


PINNACLE_API_URL = "https://www.pinnacle.com/config/app.json"
PINNACLE_MATCHUPS_URL = (
    "https://guest.api.arcadia.pinnacle.com/0.1/leagues/487/matchups?brandId=0"
)


def get_api_key():
    """Fetch the API key from Pinnacle."""
    try:
        response = requests.get(PINNACLE_API_URL)
        response.raise_for_status()
        return response.json()["api"]["haywire"]["apiKey"]
    except (RequestException, KeyError) as e:
        print(f"Error fetching API key: {e}")
        return None


def get_headers(api_key):
    """Generate headers for requests."""
    return {
        "accept": "application/json",
        "origin": "https://www.pinnacle.com",
        "referer": "https://www.pinnacle.com/",
        "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "x-api-key": api_key,
        "x-device-uuid": "a95be666-e4a9ef8e-d52b73dd-0d559878",
    }


def fetch_matchups(headers):
    """Fetch matchups from Pinnacle."""
    try:
        response = requests.get(PINNACLE_MATCHUPS_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"Error fetching matchups: {e}")
        return []


def filter_nba_matchups(matchups):
    """Filter NBA matchups."""
    return {
        matchup["id"]: {
            "home_name": matchup["participants"][0]["name"],
            "away_name": matchup["participants"][1]["name"],
            "start_time": matchup["startTime"],
        }
        for matchup in matchups
        if matchup["league"]["name"] == "NBA" and matchup["type"] != "special"
    }


def fetch_game_odds(matchup_id, headers):
    """Fetch game odds for a specific matchup."""
    url = f"https://guest.api.arcadia.pinnacle.com/0.1/matchups/{matchup_id}/markets/related/straight"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"Error fetching game odds for matchup {matchup_id}: {e}")
        return []


def process_game_odds(game_odds):
    """Process game odds and filter relevant data."""
    return {
        odds["key"]: {
            "prices": odds["prices"],
            "side": odds.get("side"),
            "type": odds["type"],
        }
        for odds in game_odds
        if ";0;" in odds["key"] and not odds.get("isAlternate", True)
    }


def main():
    api_key = get_api_key()
    if not api_key:
        return

    headers = get_headers(api_key)
    matchups = fetch_matchups(headers)
    matchups_dict = filter_nba_matchups(matchups)

    game_odds_dict = {}
    for matchup_id, data in matchups_dict.items():
        print(matchup_id, data)
        game_odds = fetch_game_odds(matchup_id, headers)
        game_odds_dict[matchup_id] = process_game_odds(game_odds)

    for matchup_id, odds in game_odds_dict.items():
        print(matchup_id)
        for key, data in odds.items():
            print(key, data)
        input()


if __name__ == "__main__":
    main()

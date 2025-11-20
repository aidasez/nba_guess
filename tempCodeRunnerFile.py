game_match = next((g for g in games if g[0]['home_team'] == home_team_name and g[1]['away_team'] == away_team_name), None)
        if not game_match:
            continue
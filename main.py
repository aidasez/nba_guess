import requests
import json
from datetime import datetime
import os
import subprocess
spreads = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey=444beff304152507097f09cc2d6a2751&regions=uk&markets=spreads"
moneyline = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey=444beff304152507097f09cc2d6a2751&regions=uk&markets=h2h"
response_spreads = requests.get(spreads)
response_spreads = response_spreads.json()
response_moneyline = requests.get(moneyline)
response_moneyline = response_moneyline.json()
date = datetime.now().strftime("%Y-%m-%d")
month = datetime.now().strftime("%m")
yesterday = int(datetime.now().strftime("%d")) - 1
def generate_index_html(base_dir=None):
    """
    Generates an index.html in the base_dir that links to all *_games.html files
    inside subfolders named with dates (ISO format).
    """
    if base_dir is None:
        base_dir = os.getcwd()

    # Find all folders in base_dir
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
    folders.sort(reverse=True)  # latest first

    # Start building the index HTML
    index_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NBA Games Index</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 50px;
            }
            h1 {
                margin-bottom: 30px;
            }
            .button-container {
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                justify-content: center;
            }
            .button-container a {
                text-decoration: none;
                background-color: #4CAF50;
                color: white;
                padding: 15px 25px;
                border-radius: 8px;
                font-size: 16px;
                transition: background-color 0.3s ease;
            }
            .button-container a:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <h1>NBA Games</h1>
        <div class="button-container">
    """

    total_files = 0
    # Loop through folders
    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        # Find *_games.html files
        html_files = [f for f in os.listdir(folder_path) if f.endswith("_games.html")]
        for html_file in html_files:
            relative_path = os.path.join(folder, html_file)
            # Use folder name (date) as button text
            button_text = folder
            index_html += f'            <a href="{relative_path}" target="_blank">{button_text}</a>\n'
            total_files += 1

    # Close HTML
    index_html += """
        </div>
    </body>
    </html>
    """

    # Write index.html to base_dir
    with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"index.html generated in {base_dir} with {total_files} game files from {len(folders)} folders.")
def upload_to_github(repo_dir, commit_message="Update NBA HTML files"):
    """
    Commits and pushes all changes in the specified repo_dir to GitHub.

    Parameters:
    - repo_dir: str, path to your git repository
    - commit_message: str, message for the commit
    """
    # Change working directory to the repo
    cwd = os.getcwd()
    os.chdir(repo_dir)

    try:
        # Stage all changes
        subprocess.run(["git", "add", "."], check=True)

        # Commit changes
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Push to the remote repository (default 'origin' and current branch)
        subprocess.run(["git", "push"], check=True)

        print("Successfully pushed changes to GitHub!")
    except subprocess.CalledProcessError as e:
        print("Error during git operations:", e)
    finally:
        # Return to original directory
        os.chdir(cwd)
def save_file():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(date, exist_ok=True)
    os.chdir(date)
    with open(f"{date}_moneyline.json","w") as json_file:
        json.dump(response_moneyline,json_file,indent=4)
    with open(f"{date}_spreads.json","w") as json_file:
        json.dump(response_spreads,json_file,indent=4)
    create_html()
    os.chdir(script_dir)
def create_html():
    html_parent = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{date}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 10px;
            }}
            .game-box {{
                background-color: #fff;
                border: 2px solid #333;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
                width: fit-content;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
                display: inline-block;         
                max-width: 90%;  
                word-wrap: break-word;
            }}
            .game-box h2 {{
                margin: 0 0 10px 0;
                font-size: 18px;
                text-align: center;      
                width: 100%;  
            }}
            .game-box p {{
                margin: 5px 0;
            }}
        </style>
    </head>
    <body>
    """
    for i in range(0,len(games)):
        if games[i][2] > 0 :
            plusminus = "+"
        else:
            plusminus = ""
        success_overall_winner = "?"
        success_spread_winner = "?"
        html_parent += f"""
        <div class="game-box">
        <h2>{games[i][0]["home_team"]}
        <p><em>  {games[i][0]["odds"]}</p></em> 
        {games[i][1]["away_team"]}
        <p><em>  {games[i][1]["odds"]}</p></em></h2>
        <p><strong>Spread: {plusminus}{games[i][2]}</strong></p>
        <p><strong>Odds of Spread:</strong> {games[i][3]}</p>
        <p><strong>Success: </strong> Overall: {success_overall_winner}, Spread: {success_spread_winner}  </p>
        </div>
        """
    html_parent += """
    </body>
    </html>
    """
    with open(f"{date}_games.html", "w") as f:
        f.write(html_parent)
def update_html(date):
    success_list = find_outcome(date)

    with open(f"{date}_games.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    # Replace each placeholder in order
    for overall, spread in success_list:
        html_content = html_content.replace(
            "Overall: ?, Spread: ?", 
            f"Overall: {overall}, Spread: {spread}", 
            1
        )

    # Save updated HTML
    with open(f"{date}_games.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    
        
            
def find_outcome(date):
    # Load scores
    results_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/scores/?apiKey=444beff304152507097f09cc2d6a2751&dateFormat={date}"
    response_result = requests.get(results_url).json()

    success_list = []

    for i in range(len(response_result)):
        # Get scores
        home_score = int(next(s['score'] for s in response_result[i]['scores'] if s['name'] == games[i][0]['home_team']))
        away_score = int(next(s['score'] for s in response_result[i]['scores'] if s['name'] == games[i][1]['away_team']))

        # Determine overall winner
        overall_winner = "home" if home_score > away_score else "away"

        # Determine favourite by moneyline odds
        favourite = "home" if games[i][0]["odds"] > games[i][1]["odds"] else "away"

        # Determine spread winner
        spread = games[i][3]
        if favourite == "home":
            spread_winner = "home" if (home_score - spread) > away_score else "away"
        else:
            spread_winner = "home" if (home_score) > (away_score - spread) else "away"

        # Save success
        success_list.append([overall_winner, spread_winner])

    return success_list

            
            
        
        
    
    
def get_response_api():
    for i in range (0,len(response_moneyline)):
        print(i)
        favourite = 0
        home_team = response_spreads[i]["home_team"]
        away_team = response_spreads[i]["away_team"]
        hname = home_team[0]
        temp = response_moneyline[i]["bookmakers"][0]["markets"][0]["outcomes"][0]
        print("temp",temp)
        temp = list(temp.values())[0][0]
        print("temp",temp)
        print("hname",hname)
        
        if temp == hname:
            home_odds_moneyline = response_moneyline[i]["bookmakers"][0]["markets"][0]["outcomes"][favourite]["price"]
            away_odds_moneyline = response_moneyline[i]["bookmakers"][0]["markets"][0]["outcomes"][favourite+1]["price"]
        else:
            home_odds_moneyline = response_moneyline[i]["bookmakers"][0]["markets"][0]["outcomes"][favourite+1]["price"]
            away_odds_moneyline = response_moneyline[i]["bookmakers"][0]["markets"][0]["outcomes"][favourite]["price"]
        home = {
            "home_team": home_team,
            "odds": home_odds_moneyline
        }
        away = {
            "away_team": away_team,
            "odds": away_odds_moneyline
        }
        if home_odds_moneyline > away_odds_moneyline:
            favourite = 1
        spread  = response_spreads[i]["bookmakers"][0]["markets"][0]["outcomes"][favourite]["point"]
        
        odds_spread = response_spreads[i]["bookmakers"][0]["markets"][0]["outcomes"][favourite]["price"]
        
        games.append([home,away,spread,odds_spread])

    return games
games = []
games = get_response_api()
save_file()
# update_html(f"2025-{month}-{yesterday}")
generate_index_html()
repo_dir = "C:\handicap_guess"
upload_to_github(repo_dir)
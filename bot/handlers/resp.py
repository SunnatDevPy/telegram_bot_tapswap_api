import http.client
from datetime import datetime
from aiogram import html
import pytz
import requests


def change_timezone(iso_date_str):
    dt_utc = datetime.fromisoformat(iso_date_str)

    local_tz = pytz.timezone('Asia/Tashkent')
    dt_local = dt_utc.astimezone(local_tz)

    formatted_date_str = dt_local.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_date_str


def get_response(part_url, querystring=None):
    conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "666fb3a3f0mshd6f49ac99388165p10de96jsn4e667b43a669",
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
    }
    conn.request("GET", "/v2/odds/league/865927/bookmaker/5?page=2", headers=headers)
    url = f"https://api-football-v1.p.rapidapi.com/v3/{part_url}"

    # querystring = {"country": "England"} -> angliya ligalari
    response = requests.get(url, headers=headers, params=querystring if querystring else None)
    return response.json()


def live_game(res, id):
    list_ = []
    about = {}
    data = res['response']
    count = 1
    for i in data:
        league = i['league']
        if league['id'] == id:
            text = html.bold(f'''
⌛Boshlangan vaqti (Toshkent): {change_timezone(i['fixture']['date'])}
Bosqich: {league['round']}

🏠Uyda: {i['teams']['home']['name']}
Goal: {html.code(i['goals']['home'] if i['goals']['home'] else 0)}

🤼Mehmonda: {i['teams']['away']['name']}
Goal: {html.code(i['goals']['away'] if i['goals']['away'] else 0)}''')
            list_.append(text)
            about[str(count)] = html.bold(team_goal(league, i.get('events'), i['teams'], i['goals'], i['score']))
            count += 1
    return list_, about


def team_goal(league, events, teams, goals, score):
    home = f"""
🏠Uyda {teams['home']['name']}:
Goal: {goals['home'] if goals['home'] else 0}
Penalty: {score['penalty']['home'] if score['penalty']['home'] else 0}
Extra time: {score['extratime']['home'] if score['extratime']['home'] else 0}
"""
    away = f"""
🤼Mehmonda {teams['away']['name']}:
Goal: {goals['away'] if goals['away'] else 0}
Penalty: {score['penalty']['home'] if score['penalty']['home'] else 0}
Extra time: {score['extratime']['home'] if score['extratime']['home'] else 0}
"""
    if events:
        for i in events:
            type = "Goal urdi" if i['type'] == "Goal" else f"{i['detail']} oldi"

            assist = f"Assist: {i['assist']['name']} \n\n" if i['assist']['name'] else " "
            extra = f"Extra Time: " if i['time']['extra'] else "Time: "
            if i['team']["id"] == teams['home']["id"]:
                home += '=========================================\n'
                home += f'{extra}{i["time"]["elapsed"]} \n'
                home += f"Player: {i['player']['name']} {type}\n"
                home += assist
            else:
                away += '=========================================\n'
                away += f'{extra}{i["time"]["elapsed"]} \n'
                away += f"Player: {i['player']['name']} {type}\n"
                away += assist
    return home + '\n' + away

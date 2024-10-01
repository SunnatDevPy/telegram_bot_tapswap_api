import http.client
from datetime import datetime

import pytz
import requests
from aiogram import html
from aiogram.utils.i18n import gettext as _


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
            boshlanish = _("⌛Boshlangan vaqti (Toshkent)")
            bosqich = _("Bosqich")
            home = _("Uyda")
            gol = _("Goal")
            mehmin = _("Mehmonda")
            text = html.bold(f'''
{boshlanish}: {change_timezone(i['fixture']['date'])}
{boshlanish}: {league['round']}

🏠{home}: {i['teams']['home']['name']}
{gol}: {html.code(i['goals']['home'] if i['goals']['home'] else 0)}

🤼{mehmin}: {i['teams']['away']['name']}
{gol}: {html.code(i['goals']['away'] if i['goals']['away'] else 0)}''')
            list_.append(text)
            about[str(count)] = html.bold(team_goal(league, i.get('events'), i['teams'], i['goals'], i['score']))
            count += 1
    return list_, about


def team_goal(league, events, teams, goals, score):
    boshlanish = _("⌛Boshlangan vaqti (Toshkent)")
    bosqich = _("Bosqich")
    homep = _("Uyda")
    gol = _("Goal")
    mehmin = _("Mehmonda")
    penalty = _("Penalty")
    extras = _("Extra time")
    home = f"""
🏠{homep} {teams['home']['name']}:
{gol}: {goals['home'] if goals['home'] else 0}
{penalty}: {score['penalty']['home'] if score['penalty']['home'] else 0}
{extras}: {score['extratime']['home'] if score['extratime']['home'] else 0}
"""
    away = f"""
🤼{mehmin} {teams['away']['name']}:
{gol}: {goals['away'] if goals['away'] else 0}
{penalty}: {score['penalty']['home'] if score['penalty']['home'] else 0}
{extras}: {score['extratime']['home'] if score['extratime']['home'] else 0}
"""
    if events:
        goals = _("Goal urdi")
        oldi = _("oldi")
        for i in events:
            type = goals if i['type'] == gol else f"{i['detail']} {oldi}"

            assist = f"Assist: {i['assist']['name']} \n\n" if i['assist']['name'] else " "
            extra = f"{extras}: " if i['time']['extra'] else "Time: "
            player = _("Player")
            if i['team']["id"] == teams['home']["id"]:
                home += '=========================================\n'
                home += f'{extra}{i["time"]["elapsed"]} \n'
                home += f"{player}: {i['player']['name']} {type}\n"
                home += assist
            else:
                away += '=========================================\n'
                away += f'{extra}{i["time"]["elapsed"]} \n'
                away += f"{player}: {i['player']['name']} {type}\n"
                away += assist
    return home + '\n' + away

from datetime import datetime
from sys import argv
from os.path import join
import json

import settings
from league import League
from tournaments import get_tournament_from_url
from template import generate_static_html


def get_lines(file_name):
    file = open(file_name, "r")
    text = file.read()
    file.close()

    return [l for l in text.split("\n") if l]


def get_alts(file_name):
    alts = {}

    for line in get_lines(file_name):
        if line:
            names = [League.get_check_str(n) for n in line.split(" ")]
            for n in names[1:]:
                alts[n] = names[0]

    return alts


def save_html(league, file_name, css_file, provisional_games):
    file_name = file_name.replace(".json", ".html")
    html = open(join("html", file_name), "w")
    html.write(generate_static_html(
        league.get_json_data(), css_file,
        provisional_games
    ))


def save_json(league, file_name):
    file = open(join("json", file_name), "w")
    json.dump(league.get_json_data(), file, indent=4)
    file.close()


def get_league(file_name):
    try:
        file = open(join("json", file_name))
        json_data = json.load(file)
        file.close()

        return League.get_from_json(json_data)

    except FileNotFoundError:
        return League(settings.LEAGUE_NAME)


def get_tourney_args(file_name):
    tourneys = []

    for line in get_lines(file_name):
        if " " in line:
            line = line.split(" ")
            url = line[0]
            strength = float(line[1])
        else:
            url = line
            strength = 1

        tourneys.append(
            (url, strength)
        )

    return tourneys


def get_rankings(league, tourney_file, alts, follow):
    args = []

    for a in get_tourney_args(tourney_file):
        url, strength = a

        if not league.check_tourney_url(url):
            args.append(a)

    tourneys = [
        get_tournament_from_url(a[0], a[1], alts=alts) for a in args
    ]

    for t in tourneys:
        league.add_tournament(t, player_list=follow)

    league.apply_season_elo()


if __name__ == "__main__":
    style_sheet = settings.CSS_FILE
    league_name = settings.LEAGUE_NAME
    league_alts = get_alts(settings.ALTS_FILE)

    league_file = None
    player_list = None
    html_file = None
    force_reset = False

    for arg in argv:
        if ".css" in arg:
            style_sheet = arg

        if ".json" in arg:
            league_file = arg

        if ".html" in arg:
            html_file = arg

        if arg == "follow":
            player_list = get_lines(settings.FOLLOW_FILE)

        if arg == "save":
            time = datetime.now().isoformat().replace(":", "")
            league_file = league_name.replace(" ", "_") + time + ".json"

        if arg == "html":
            html_file = True

        if arg == "f":
            force_reset = True

    if league_file and not force_reset:
        league_obj = get_league(league_file)
    else:
        league_obj = League(settings.LEAGUE_NAME)

    get_rankings(
        league_obj, settings.TOURNEY_FILE,
        league_alts,
        follow=player_list
    )

    if html_file:
        if html_file is True:
            time = datetime.now().isoformat().replace(":", "")
            html_file = league_obj.name + time + ".html"

        save_html(
            league_obj, html_file, style_sheet,
            settings.PROVISIONAL_GAMES
        )

    if league_file:
        save_json(league_obj, league_file)

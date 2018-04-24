from datetime import datetime
from sys import argv
from os.path import join

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
            names = line.split(" ")
            for n in names[1:]:
                alts[n] = names[0]

    return alts


def get_rankings(league_name, tournaments, alts, follow, css_file, provisional_games):
    league = League(league_name)

    for url in tournaments:
        t = get_tournament_from_url(url, alts=alts)
        league.add_tournament(t, player_list=follow)

    file_name = league_name.replace(" ", "_") + datetime.now().isoformat().replace(":", "")
    league.save_league_data(file_name)

    html = open(join("html", file_name + ".html"), "w")
    html.write(generate_static_html(
        league.get_json_data(), css_file,
        provisional_games
    ))

if __name__ == "__main__":
    tourneys = get_lines(settings.TOURNEY_FILE)
    league_alts = get_alts(settings.ALTS_FILE)

    if "follow" in argv:
        player_list = get_lines(settings.FOLLOW_FILE)
    else:
        player_list = False

    style_sheet = settings.CSS_FILE
    for arg in argv:
        if ".css" in arg:
            style_sheet = arg

    get_rankings(
        settings.LEAGUE_NAME,
        tourneys,
        league_alts,
        player_list,
        style_sheet,
        settings.PROVISIONAL_GAMES
    )

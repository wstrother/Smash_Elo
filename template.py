
def get_player_element(player, rank, p=0):
    tag = player["tag"]
    rating = player["rating"]
    g_wins = player["games_won"]
    g_losses = player["games_lost"]
    s_wins = player["sets_won"]
    s_losses = player["sets_lost"]

    def get_rate_div(css_class, noun, wins, losses):
        wins_span = "<span class='rate-number'>{}</span>".format(wins)
        total_span = "<span class='rate-number'>{}</span>".format(wins + losses)
        rate_span = "<span class='rate-percentage'>({:0.2f})</span>".format(wins / (wins + losses))

        grd = "{} wins / {} {} {}".format(wins_span, total_span, noun, rate_span)

        return get_div(css_class, grd, t=2)

    # <league_player_div>
    #   <player_main_div>
    #       <rank_div />
    rank_div = get_div("player_rank_div", rank, t=2)

    #       <tag_div />
    tag_div = get_div("player_tag_div", tag, t=2)

    #   </player_main_div>
    player_main_div = get_div("player_main_div", rank_div + tag_div)

    #   <player_rating_div />
    player_rating_div = get_div("player_rating_div", round(rating), t=1)

    #   <player_rates_div>
    #       <game_rate_div />
    game_rate_div = get_rate_div("game_rate_div", "games", g_wins, g_losses)

    #       <set_rate_div />
    set_rate_div = get_rate_div("set_rate_div", "sets", s_wins, s_losses)

    #   </player_rates_div>
    player_rates_div = get_div("player_rates_div", game_rate_div + set_rate_div)

    body = player_main_div + player_rating_div + player_rates_div

    class_name = "league_player_div"
    if p and (g_wins + g_losses) < p:
        class_name += " provisional_player"

    return "\n\n" + get_div(class_name, body)


def get_match_element(match):
    winner = match["winner"]
    loser = match["loser"]
    w_old = match["winner_elo"]
    l_old = match["loser_elo"]
    dv = match["applied_change"]
    w_new = w_old + dv
    l_new = l_old - dv
    wins, losses = match["winner_games"], match["loser_games"]

    def get_elo_div(old, new):
        old_span = "<span class='{}'>{:0.0f}</span>".format("elo-number", old)
        new_span = "<span class='{}'>{:0.0f}</span>".format("elo-number", new)
        arrow_span = "<span class='{}'>{}</span>".format("elo-arrow", "->")

        ged = old_span + arrow_span + new_span

        return get_div("elo-change", ged, t=2)

    def get_player_div(tag, css_class, label, old, new):
        label_div = get_div("match_results_div", label, t=2)
        tag_div = get_div("match_tag_div", tag, t=2)
        elo_div = get_elo_div(old, new)

        gpd = label_div + tag_div + elo_div

        return get_div(css_class, gpd, t=1)

    # <league_match_div>
    #   <winner_div>
    #       <match_results_div />
    #       <match_tag_div />
    #       <match_elo_div />
    #   </winner_div>
    winner_div = get_player_div(
        winner, "match_winner_div", "winner", w_old, w_new
    )

    #   <set_count_div />
    set_count_div = get_div(
        "set_count_div",
        "{} - {}".format(wins, losses),
        t=1
    )

    #   <loser_div>
    #       <match_results_div />
    #       <match_tag_div />
    #       <match_elo_div />
    #   </loser_div>
    loser_div = get_player_div(
        loser, "match_loser_div", "loser", l_old, l_new
    )

    # </league_match_div>
    body = winner_div + set_count_div + loser_div

    return "\n\n" + get_div("league_match_div", body)


def get_tournament_element(tournament):
    # <league_tournament_div>
    #   <tournament_name_div />
    name_div = get_div("tournament_name_div", tournament["name"], t=1)

    #   <tournament_date_div />
    date_div = get_div("tournament_date_div", tournament["date"], t=1)

    #   <bracket_link_div />
    url = tournament["url"]
    link = "<a href='{}'>{}</a>".format(url, "View Bracket")
    link_div = get_div("bracket_link_div", link)

    # </league_tournament_div>
    body = name_div + date_div + link_div

    return "\n\n" + get_div("league_tournament_div", body)


def get_div(class_name, body, t=0):

    return "{}<div class='{}'>\n{}{}\n{}</div>\n".format(
        "\t" * t, class_name,
        "\t" * (t + 1), body,
        "\t" * t
    )


def generate_static_html(league_data, css_file, provisional_games=None):
    title = league_data["name"]
    stylesheet = "<link rel='stylesheet' href='{}' />".format(css_file)
    head = "<head>\n<title>{}</title>\n{}\n</head>".format(title, stylesheet)

    players = league_data["players"]
    players = sorted(players, key=lambda p: p["rating"], reverse=True)

    player_html = ""
    i = 1
    for p in players:
        player_html += get_player_element(p, i, p=provisional_games)
        i += 1

    tournaments = league_data["tournaments"]

    matches_html = ""
    for t in tournaments:
        matches_html += get_tournament_element(t)

        matches = [m for m in league_data["matches"] if m["tournament"] == t["name"]]

        for m in matches:
            matches_html += get_match_element(m)

    body = "<body>\n{}\n</body>".format(player_html + matches_html)

    html = "<html>{}\n\n{}\n</html>".format(head, body)

    return html

import json
from os.path import join

from settings import ELO_WIDTH, START_ELO, K_FACTOR
import elo


class Player:
    ID = 0

    def __init__(self, tag, rating):
        self.id = Player.ID
        Player.ID += 1

        self.tag = tag
        self.display_name = tag
        self.rating = rating

        self.games_won = 0
        self.games_lost = 0
        self.sets_won = 0
        self.sets_lost = 0

    def __str__(self):
        return self.display_name

    @staticmethod
    def get_from_json(json_data):
        player = Player(
            json_data["tag"],
            json_data["rating"]
        )

        player.games_won = json_data["games_won"]
        player.games_lost = json_data["games_lost"]
        player.sets_won = json_data["sets_won"]
        player.sets_lost = json_data["sets_lost"]
        player.display_name = json_data["display_name"]
        player.id = json_data["id"]

        return player


class Match:
    ID = 0

    def __init__(self, winner, loser, set_count, tournament, strength=1):
        self.id = Match.ID
        self.elo_applied = False
        Match.ID += 1

        self.tournament = tournament
        self.winner = winner
        self.winner_elo = 0
        self.loser = loser
        self.loser_elo = 0

        self.winner_games, self.loser_games = set_count
        self.strength = strength
        self.elo_width = ELO_WIDTH
        self.k_factor = K_FACTOR

    def __str__(self):
        return "{} > {} ({} - {})".format(
            self.winner, self.loser, *self.set_count
        )

    def get_json_data(self):
        return {
            "id": self.id,
            "winner": self.winner,
            "winner_elo": self.winner_elo,
            "winner_games": self.winner_games,
            "loser": self.loser,
            "loser_elo": self.loser_elo,
            "loser_games": self.loser_games,
            "winner_change": self.winner_change,
            "loser_change": self.loser_change,
            "applied_change": self.applied_change,
            "tournament": self.tournament,
            "strength": self.strength,
            "elo_applied": self.elo_applied
        }

    @staticmethod
    def get_from_json(json_data):
        match = Match(
            json_data["winner"],
            json_data["loser"],
            (json_data["winner_games"], json_data["loser_games"]),
            json_data["tournament"],
            json_data["strength"]
        )
        match.winner_elo = json_data["winner_elo"]
        match.loser_elo = json_data["loser_elo"]
        match.elo_applied = json_data["elo_applied"]
        match.id = json_data["id"]

        return match

    @property
    def set_count(self):
        return self.winner_games, self.loser_games

    @property
    def winner_change(self):
        return elo.get_elo_change(
            self.winner_elo,
            self.loser_elo,
            self.elo_width,
            self.k_factor * self.strength,
        )

    @property
    def loser_change(self):
        return elo.get_elo_change(
            self.loser_elo,
            self.winner_elo,
            self.elo_width,
            self.k_factor * self.strength,
        )

    @property
    def applied_change(self):
        return (self.winner_change * self.winner_games) - (self.loser_change * self.loser_games)


class League:
    def __init__(self, name):
        self.name = name
        self.players = {}
        self.matches = []
        self.tournaments = []

        self.elo_width = ELO_WIDTH
        self.k_factor = K_FACTOR
        self.start_rating = START_ELO

    def __str__(self):
        return self.name

    @staticmethod
    def get_from_json(json_data):
        name = json_data["name"]
        league = League(name)
        league.elo_width = json_data["elo_width"]
        league.k_factor = json_data["k_factor"]
        league.start_rating = json_data["start_rating"]

        league.tournaments = json_data["tournaments"]
        league.matches = [
            Match.get_from_json(m) for m in json_data["matches"]
        ]
        league.players = {
            p["tag"]: Player.get_from_json(p) for p in json_data["players"]
        }

        return league

    def get_json_data(self):
        return {
            "name": self.name,
            "elo_width": self.elo_width,
            "k_factor": self.k_factor,
            "start_rating": self.start_rating,
            "players": [p.__dict__ for p in self.players.values()],
            "matches": [m.get_json_data() for m in self.matches],
            "tournaments": self.tournaments
        }

    def get_player_by_tag(self, tag):
        check_str = self.check_tag(tag)

        if tag not in self.players:
            self.players[check_str] = Player(tag, self.start_rating)

        return self.players[check_str]

    def add_tournament(self, tournament, player_list=None):
        include = True
        for t in self.tournaments:
            if t["name"] == tournament.name:
                include = False

        if include:
            print("\n Adding {} to {}".format(tournament, self))
            self.tournaments.append(tournament.get_json_data())

            self.matches += tournament.get_match_list(
                    player_list=player_list
            )

    def apply_season_elo(self):
        for t in self.tournaments:
            print("\nApplying matches from {}".format(t["name"]))

            matches = [m for m in self.matches if m.tournament == t["name"]]
            for m in matches:
                self.apply_match_elo(m)

        players = sorted(self.players.values(), key=lambda p: p.rating, reverse=True)

        print("\n---")
        for player in players:
            print("{:>30}: \t{}".format(player.tag, player.rating))

    def apply_match_elo(self, match):
        if not match.elo_applied:
            print("\nApplying match: {}".format(match))
            winner = self.get_player_by_tag(match.winner)
            loser = self.get_player_by_tag(match.loser)

            match.winner_elo = winner.rating
            match.loser_elo = loser.rating

            dv = match.applied_change
            wins, losses = match.set_count
            winner.rating += dv
            loser.rating -= dv

            winner.games_won += wins
            winner.games_lost += losses
            winner.sets_won += 1

            loser.games_won += losses
            loser.games_lost += wins
            loser.sets_lost += 1

            match.elo_applied = True
            print("\t{} {} -> {}".format(winner.tag, match.winner_elo, winner.rating))
            print("\t{} {} -> {}".format(loser.tag, match.loser_elo, loser.rating))

    @staticmethod
    def check_tag(tag, alts=None):
        tag = League.get_check_str(tag)

        if alts and tag in alts:
            tag = alts[tag]

        return tag

    @staticmethod
    def get_check_str(tag):
        return "".join([c for c in tag.upper() if c.isalnum()])

    def check_tourney_url(self, url):
        for t in self.tournaments:
            if url == t["url"]:
                return True


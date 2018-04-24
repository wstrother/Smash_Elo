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
            "tournament": self.tournament
        }

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

    # def get_player_by_id(self, value):
    #     for player in self.players.values():
    #         if player.id == value:
    #             return player

    def get_player_by_tag(self, tag):
        check_str = self.check_tag(tag)

        if tag not in self.players:
            self.players[check_str] = Player(tag, self.start_rating)

        return self.players[check_str]

    # def add_match(self, winner, loser, set_count, tournament, strength=1):
    #     winner = self.get_player_by_tag(winner)
    #     loser = self.get_player_by_tag(loser)
    #     match = Match(
    #         winner, loser, set_count,
    #         tournament, strength=strength
    #     )
    #
    #     self.apply_match_elo(match)
    #     self.matches.append(match)

    def add_tournament(self, tournament, strength=1, player_list=None):
        print("\n Adding {} to {}".format(tournament, self))
        self.tournaments.append(tournament.get_json_data())

        matches = tournament.get_match_list(
                strength=strength, player_list=player_list
        )

        for match in matches:
            self.apply_match_elo(match)

    def apply_match_elo(self, match):
        self.matches.append(match)

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

    def save_league_data(self, file_name):
        file = open(join("league_data", file_name + ".json"), "w")
        json.dump(self.get_json_data(), file, indent=4)
        file.close()

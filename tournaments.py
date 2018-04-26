import challonge

from settings import CHALLONGE_USERNAME, CHALLONGE_API_KEY
from league import League, Match


def get_tournament_from_url(url, strength, alts=None):
    if " " in url:
        pass

    if "challonge.com" in url:
        return ChallongeTournament(url, strength, alts=alts)

    # if "smash.gg" in url:
    #     return SmashggTournament(url, alts=alts)


class ChallongeTournament:
    challonge.set_credentials(CHALLONGE_USERNAME, CHALLONGE_API_KEY)

    def __init__(self, url, strength, alts=None):
        name = url.split("/")[-1]
        self.name = name
        self.url = url
        self.strength = strength
        self.alts = alts

        print("\nRetrieving data from {}".format(url))
        self.date = challonge.tournaments.show(name)["started-at"].isoformat()
        self.participants = challonge.participants.index(name)
        self.matches = challonge.matches.index(name)

    def __str__(self):
        return "Challonge tournament: {}".format(self.name)

    def get_json_data(self):
        return {
            "name": self.name,
            "url": self.url,
            "date": self.date
        }

    def get_tag_by_id(self, value):
        for p in self.participants:
            if p["id"] == value:
                return League.check_tag(
                    p["name"], alts=self.alts
                )

    def get_match_list(self, player_list=None):
        matches = []
        if player_list:
            player_list = [League.get_check_str(n) for n in player_list]

        for match in self.matches:
            # check names against alts
            winner_tag = self.get_tag_by_id(match["winner-id"])
            loser_tag = self.get_tag_by_id(match["loser-id"])

            # check data is complete
            include = winner_tag and loser_tag  # True unless
            #                                     Challonge data is incomplete

            # check names to include list
            if player_list:
                include = winner_tag in player_list and loser_tag in player_list

            # convert to league data
            if include:
                matches.append(self.get_match_object(match))

        return matches

    def get_match_object(self, match):
        winner_tag = self.get_tag_by_id(match["winner-id"])
        loser_tag = self.get_tag_by_id(match["loser-id"])

        set_count = match["scores-csv"]
        if set_count:
            w, l = sorted([int(x) for x in set_count.split("-")], reverse=True)
            set_count = w, l
        else:
            set_count = 1, 0

        return Match(
            winner_tag, loser_tag,
            set_count, self.name,
            strength=self.strength
        )

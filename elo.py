# this code adapted from https://www.kaggle.com/kplauritzen/elo-ratings-in-python


def get_elo_change(winner_elo, loser_elo, elo_width, k_factor):
    """
    https://en.wikipedia.org/wiki/Elo_rating_system#Mathematical_details
    """

    expected_win = expected_result(winner_elo, loser_elo, elo_width)
    change_in_elo = k_factor * (1-expected_win)

    return change_in_elo


def expected_result(elo_a, elo_b, elo_width):
    """
    https://en.wikipedia.org/wiki/Elo_rating_system#Mathematical_details
    """
    expect_a = 1.0/(1+10**((elo_b - elo_a)/elo_width))

    return expect_a

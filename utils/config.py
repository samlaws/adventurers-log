import string


def format_sel(label):
    return string.capwords(label.replace("_", " ")).replace("Rank", "rank")

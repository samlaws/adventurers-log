import string
import streamlit as st


def format_sel(label):
    return string.capwords(label.replace("_", " ")).replace("Rank", "rank")


def format_sel_boss(label):
    return boss_dict[label]


def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()),
                    unsafe_allow_html=True)


boss_dict = {
    "abyssal_sire": "Abyssal Sire",
    "alchemical_hydra": "Alchemical Hydra",
    "barrows_chests": "Barrows Chests",
    "bryophyta": "Bryophyta",
    "callisto": "Callisto",
    "cerberus": "Cerberus",
    "chambers_of_xeric": "CoX",
    "chambers_of_xeric_challenge_mode": "CoX CM",
    "chaos_elemental": "Chaos Elemental",
    "chaos_fanatic": "Chaos Fanatic",
    "commander_zilyana": "Zilyana",
    "corporeal_beast": "Corporeal Beast",
    "crazy_archaeologist": "Crazy Arch",
    "dagannoth_prime": "Dag. Prime",
    "dagannoth_rex": "Dag. Rex",
    "dagannoth_supreme": "Dag. Supreme",
    "deranged_archaeologist": "Deranged Arch",
    "general_graardor": "Graardor",
    "giant_mole": "Giant Mole",
    "grotesque_guardians": "G. Guardians",
    "hespori": "Hespori",
    "kalphite_queen": "Kalphite Queen",
    "king_black_dragon": "KBD",
    "kraken": "Kraken",
    "kreearra": "Kree'arra",
    "kril_tsutsaroth": "K'ril",
    "mimic": "Mimic",
    "nightmare": "Nightmare",
    "obor": "Obor",
    "sarachnis": "Sarachnis",
    "scorpia": "Scorpia",
    "skotizo": "Skotizo",
    "tempoross": "Tempoross",
    "the_gauntlet": "Gauntlet",
    "the_corrupted_gauntlet": "Corr. Gauntlet",
    "theatre_of_blood": "Theatre Of Blood",
    "thermonuclear_smoke_devil": "Thermy",
    "tzkal_zuk": "TzKal-Zuk",
    "tztok_jad": "TzTok-Jad",
    "venenatis": "Venenatis",
    "vetion": "Vet'ion",
    "vorkath": "Vorkath",
    "wintertodt": "Wintertodt",
    "zalcano": "Zalcano",
    "zulrah": "Zulrah",
}

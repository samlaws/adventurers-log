import requests
from PIL import Image
from io import BytesIO
import streamlit as st


@st.cache()
def load_skill_icons():

    skill_layout = [[["attack", "https://oldschool.runescape.wiki/images/f/fe/Attack_icon.png?b4bce"],
                     ["hitpoints", "https://oldschool.runescape.wiki/images/9/96/Hitpoints_icon.png?a4819"],
                     ["mining", "https://oldschool.runescape.wiki/images/4/4a/Mining_icon.png?00870"]],
                    [["strength", "https://oldschool.runescape.wiki/images/1/1b/Strength_icon.png?e6e0c"], ["agility",
                                                                                                            "https://oldschool.runescape.wiki/images/8/86/Agility_icon.png?389e0"], ["smithing", "https://oldschool.runescape.wiki/images/d/dd/Smithing_icon.png?d26c5"]],
                    [["defence", "https://oldschool.runescape.wiki/images/b/b7/Defence_icon.png?ca0cd"], ["herblore",
                                                                                                          "https://oldschool.runescape.wiki/images/0/03/Herblore_icon.png?ffa9e"], ["fishing", "https://oldschool.runescape.wiki/images/3/3b/Fishing_icon.png?15a98"]],
                    [["ranged", "https://oldschool.runescape.wiki/images/1/19/Ranged_icon.png?01b0e"], ["thieving",
                                                                                                        "https://oldschool.runescape.wiki/images/4/4a/Thieving_icon.png?973fe"], ["cooking", "https://oldschool.runescape.wiki/images/d/dc/Cooking_icon.png?a0156"]],
                    [["prayer", "https://oldschool.runescape.wiki/images/f/f2/Prayer_icon.png?ca0dc"], ["crafting",
                                                                                                        "https://oldschool.runescape.wiki/images/c/cf/Crafting_icon.png?a1f71"], ["firemaking", "https://oldschool.runescape.wiki/images/9/9b/Firemaking_icon.png?45ea0"]],
                    [["magic", "https://oldschool.runescape.wiki/images/5/5c/Magic_icon.png?334cf"], ["fletching", "https://oldschool.runescape.wiki/images/9/93/Fletching_icon.png?15cda"],
                        ["woodcutting", "https://oldschool.runescape.wiki/images/f/f4/Woodcutting_icon.png?6ead4"]],
                    [["runecrafting", "https://oldschool.runescape.wiki/images/6/63/Runecraft_icon.png?c278c"], ["slayer",
                                                                                                                 "https://oldschool.runescape.wiki/images/archive/2/28/20141020205814%21Slayer_icon.png?0741e"], ["farming", "https://oldschool.runescape.wiki/images/f/fc/Farming_icon.png?558fa"]],
                    [["construction", "https://oldschool.runescape.wiki/images/f/f6/Construction_icon.png?f9bf7"],
                        ["hunter", "https://oldschool.runescape.wiki/images/d/dd/Hunter_icon.png?8762f"]]
                    ]

    for row in skill_layout:
        for skill in row:
            response = requests.get(skill[1])
            skill[1] = Image.open(BytesIO(response.content))

    print(skill_layout)
    return skill_layout


load_skill_icons()

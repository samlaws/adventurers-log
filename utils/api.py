import requests
import streamlit as st


class ApiMethods():
    base_url = "https://api.wiseoldman.net/"

    def __init__(self, username):
        self.username = username.lower()

    def check_player_exists(self, base_url=base_url):
        url = base_url + "/players/search/"
        obj = {"username": self.username}

        responses = requests.get(url, params=obj).json()
        if self.username in [x["username"] for x in responses]:
            id = list(filter(lambda x: x["username"] ==
                             self.username, responses))[0]["id"]

            return True, id

        else:
            return False, "Player not found"

    def update_player(self, base_url=base_url):
        url = base_url + "/players/track/"
        obj = {"username": self.username}
        response = requests.post(url, obj).json()

        return response

    def get_player_details(self, id, base_url=base_url):
        url = base_url + "/players/%s" % id

        responses = requests.get(url).json()

        return responses

    def get_player_achievements(self, id, base_url=base_url):
        url = base_url + "/players/%s/achievements" % id

        responses = requests.get(url).json()

        return responses

    # @st.cache()
    def get_player_snapshots(self, id, period, base_url=base_url):
        url = base_url + "/players/%s/snapshots" % id

        obj = {"period": period}
        responses = requests.get(url, params=obj).json()

        return responses

    # @st.cache()
    def get_player_deltas(self, id, period, base_url=base_url):
        url = base_url + "/players/%s/gained" % id

        obj = {"period": period}
        responses = requests.get(url, params=obj).json()

        return responses

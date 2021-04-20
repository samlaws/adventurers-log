import requests


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

    def get_player_details(self, id, base_url=base_url):
        url = base_url + "/players/%s" % id

        responses = requests.get(url).json()

        return responses


if __name__ == "__main__":
    api = ApiMethods(username="Pompelmo")
    status, msg = api.check_player_exists()
    if status:
        player_data = api.get_player_details(id=msg)
        print(player_data)

import requests
class Notify:

    @staticmethod
    def line_notify(message):

        token = 'jhK45YGO79IQ4bW2iAeXndbKkxeBRdgyOdv9N4UXRwl'
        headers = { "Authorization": "Bearer " + token }
        data = { 'message': message }

        requests.post("https://notify-api.line.me/api/notify",
        headers = headers,
        data = data)

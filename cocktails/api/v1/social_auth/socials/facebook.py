# import facebook
import requests
from rest_framework.exceptions import AuthenticationFailed


class Facebook:
    """
    Facebook class to fetch the user info and return it
    """

    # @staticmethod
    # def validate(auth_token):
    #     """
    #     validate method Queries the facebook GraphAPI to fetch the user info
    #     """
    #     try:
    #         graph = facebook.GraphAPI(access_token=auth_token)
    #         profile = graph.request('/me?fields=name,email')
    #         return profile
    #     except:
    #         return "The token is invalid or expired."

    @staticmethod
    def validate(token):
        url = f"https://graph.facebook.com/me?access_token={token}&fields=id,email,first_name,last_name"

        response = requests.get(url)

        if response.status_code != 200:
            raise AuthenticationFailed('Не удалось верифицировать токен Facebook.')

        user_data = response.json()

        if 'error' in user_data:
            raise AuthenticationFailed('Ошибка токена Facebook: ' + user_data['error']['message'])

        return user_data
# from google.auth.transport import requests
# from google.oauth2 import id_token
import requests
# from google.oauth2 import id_token
# from google.auth.transport import requests as google_requests
# from django.conf import settings
# from rest_framework.exceptions import AuthenticationFailed


class Google:
    """Google class to fetch the user info and return it"""

    @staticmethod
    def validate(id_token, access_token):
        url = f'https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token={access_token}'
        headers = {
            'Authorization': f'Bearer {id_token}'
        }
        response = requests.get(url=url, headers=headers)

        print(response.json())
        return response.json()

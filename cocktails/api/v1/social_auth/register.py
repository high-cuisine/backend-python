from apps.user.models import User
import os
from rest_framework.authtoken.models import Token


def generate_name(name):
    try:
        if name:
            split_name = name.split(' ')
            return split_name[0], split_name[1]
        return None, None
    except:
        return None, None


def register_social_user(email, name):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        first, last = generate_name(name)
        user_data = {
            'username': email,
            'email': email,
            'first_name': first,
            'last_name': last,
            'password': os.environ.get('SOCIAL_PASSWORD')
        }
        user = User.objects.create_user(**user_data)
        user.save()

    token, _ = Token.objects.get_or_create(user=user)

    return {
        'email': user.email,
        'username': user.username,
        'token': token.key
    }

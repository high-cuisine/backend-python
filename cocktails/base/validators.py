from django.core.exceptions import ValidationError

from phonenumber_field.phonenumber import PhoneNumber, to_python


def validate_international_phonenumber(value):
    """
    В валидаторе PhoneNumberField не срабатывает перевод на русский,
    поэтому пришлось переопределить класс и валидатор
    """
    phone_number = to_python(value)
    if isinstance(phone_number, PhoneNumber) and not phone_number.is_valid():
        raise ValidationError('Введенный номер телефона недействителен.', code='invalid_phone_number')

from phonenumber_field.serializerfields import PhoneNumberField as BasePhoneNumberField


class PhoneNumberField(BasePhoneNumberField):
    default_error_messages = dict(invalid='Введите действительный номер телефона.')

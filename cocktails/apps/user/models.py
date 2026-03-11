from django.contrib.admin import display
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import CharField

from apps.user.managers import UserManager
from base.fields import ForeignKey, PhoneNumberField, ChoiceArrayField, ManyToManyField
from base.models import BaseModel, CreatedAtModel, CreatedUpdatedModel
from django.utils import timezone


__all__ = [
    'TempCode',
    'User',
    'ForgetRequest',
    'Referral',
    'Point',
    'Notification',
]

"""
cocktails=# select * from auth_permission;
 id  |               name               | content_type_id |         codename
-----+----------------------------------+-----------------+---------------------------
   1 | Can add log entry                |               1 | add_logentry
   2 | Can change log entry             |               1 | change_logentry
   3 | Can delete log entry             |               1 | delete_logentry
   4 | Can view log entry               |               1 | view_logentry
   5 | Can add permission               |               2 | add_permission
   6 | Can change permission            |               2 | change_permission
   7 | Can delete permission            |               2 | delete_permission
   8 | Can view permission              |               2 | view_permission
   9 | Can add group                    |               3 | add_group
  10 | Can change group                 |               3 | change_group
  11 | Can delete group                 |               3 | delete_group
  12 | Can view group                   |               3 | view_group
  13 | Can add content type             |               4 | add_contenttype
  14 | Can change content type          |               4 | change_contenttype
  15 | Can delete content type          |               4 | delete_contenttype
  16 | Can view content type            |               4 | view_contenttype
  17 | Can add session                  |               5 | add_session
  18 | Can change session               |               5 | change_session
  19 | Can delete session               |               5 | delete_session
  20 | Can view session                 |               5 | view_session
  21 | Can add Token                    |               6 | add_token
  22 | Can change Token                 |               6 | change_token
  23 | Can delete Token                 |               6 | delete_token
  24 | Can view Token                   |               6 | view_token
  25 | Can add token                    |               7 | add_tokenproxy
  26 | Can change token                 |               7 | change_tokenproxy
  27 | Can delete token                 |               7 | delete_tokenproxy
  28 | Can view token                   |               7 | view_tokenproxy
  29 | Can add crontab                  |               8 | add_crontabschedule
  30 | Can change crontab               |               8 | change_crontabschedule
  31 | Can delete crontab               |               8 | delete_crontabschedule
  32 | Can view crontab                 |               8 | view_crontabschedule
  33 | Can add interval                 |               9 | add_intervalschedule
  34 | Can change interval              |               9 | change_intervalschedule
  35 | Can delete interval              |               9 | delete_intervalschedule
  36 | Can view interval                |               9 | view_intervalschedule
  37 | Can add periodic task            |              10 | add_periodictask
  38 | Can change periodic task         |              10 | change_periodictask
  39 | Can delete periodic task         |              10 | delete_periodictask
  40 | Can view periodic task           |              10 | view_periodictask
  41 | Can add periodic tasks           |              11 | add_periodictasks
  42 | Can change periodic tasks        |              11 | change_periodictasks
  43 | Can delete periodic tasks        |              11 | delete_periodictasks
  44 | Can view periodic tasks          |              11 | view_periodictasks
  45 | Can add solar event              |              12 | add_solarschedule
  46 | Can change solar event           |              12 | change_solarschedule
  47 | Can delete solar event           |              12 | delete_solarschedule
  48 | Can view solar event             |              12 | view_solarschedule
  49 | Can add clocked                  |              13 | add_clockedschedule
  50 | Can change clocked               |              13 | change_clockedschedule
  51 | Can delete clocked               |              13 | delete_clockedschedule
  52 | Can view clocked                 |              13 | view_clockedschedule
  53 | Can add task result              |              14 | add_taskresult
  54 | Can change task result           |              14 | change_taskresult
  55 | Can delete task result           |              14 | delete_taskresult
  56 | Can view task result             |              14 | view_taskresult
  57 | Can add chord counter            |              15 | add_chordcounter
  58 | Can change chord counter         |              15 | change_chordcounter
  59 | Can delete chord counter         |              15 | delete_chordcounter
  60 | Can view chord counter           |              15 | view_chordcounter
  61 | Can add group result             |              16 | add_groupresult
  62 | Can change group result          |              16 | change_groupresult
  63 | Can delete group result          |              16 | delete_groupresult
  64 | Can view group result            |              16 | view_groupresult
  65 | Can add Реклама                  |              17 | add_ads
  66 | Can change Реклама               |              17 | change_ads
  67 | Can delete Реклама               |              17 | delete_ads
  68 | Can view Реклама                 |              17 | view_ads
  69 | Can add Конфигурация             |              18 | add_config
  70 | Can change Конфигурация          |              18 | change_config
  71 | Can delete Конфигурация          |              18 | delete_config
  72 | Can view Конфигурация            |              18 | view_config
  73 | Can add Документ                 |              19 | add_document
  74 | Can change Документ              |              19 | change_document
  75 | Can delete Документ              |              19 | delete_document
  76 | Can view Документ                |              19 | view_document
  77 | Can add FAQ                      |              20 | add_faq
  78 | Can change FAQ                   |              20 | change_faq
  79 | Can delete FAQ                   |              20 | delete_faq
  80 | Can view FAQ                     |              20 | view_faq
  81 | Can add Комментарий              |              21 | add_comment
  82 | Can change Комментарий           |              21 | change_comment
  83 | Can delete Комментарий           |              21 | delete_comment
  84 | Can view Комментарий             |              21 | view_comment
  85 | Can add Просмотр                 |              22 | add_hit
  86 | Can change Просмотр              |              22 | change_hit
  87 | Can delete Просмотр              |              22 | delete_hit
  88 | Can view Просмотр                |              22 | view_hit
  89 | Can add Лайк                     |              23 | add_like
  90 | Can change Лайк                  |              23 | change_like
  91 | Can delete Лайк                  |              23 | delete_like
  92 | Can view Лайк                    |              23 | view_like
  93 | Can add Пользователь             |              24 | add_user
  94 | Can change Пользователь          |              24 | change_user
  95 | Can delete Пользователь          |              24 | delete_user
  96 | Can view Пользователь            |              24 | view_user
  97 | Can add Право доступа            |              25 | add_permission
  98 | Can change Право доступа         |              25 | change_permission
  99 | Can delete Право доступа         |              25 | delete_permission
 100 | Can view Право доступа           |              25 | view_permission
 101 | Can add Реферальный код          |              26 | add_referral
 102 | Can change Реферальный код       |              26 | change_referral
 103 | Can delete Реферальный код       |              26 | delete_referral
 104 | Can view Реферальный код         |              26 | view_referral
 105 | Can add Балл                     |              27 | add_point
 106 | Can change Балл                  |              27 | change_point
 107 | Can delete Балл                  |              27 | delete_point
 108 | Can view Балл                    |              27 | view_point
 109 | Can add Восстановление пароля    |              28 | add_forgetrequest
 110 | Can change Восстановление пароля |              28 | change_forgetrequest
 111 | Can delete Восстановление пароля |              28 | delete_forgetrequest
 112 | Can view Восстановление пароля   |              28 | view_forgetrequest
 113 | Can add Платеж через Tinkoff     |              29 | add_tinkoffpayment
 114 | Can change Платеж через Tinkoff  |              29 | change_tinkoffpayment
 115 | Can delete Платеж через Tinkoff  |              29 | delete_tinkoffpayment
 116 | Can view Платеж через Tinkoff    |              29 | view_tinkoffpayment
 117 | Can add Ингредиент               |              30 | add_ingredient
 118 | Can change Ингредиент            |              30 | change_ingredient
 119 | Can delete Ингредиент            |              30 | delete_ingredient
 120 | Can view Ингредиент              |              30 | view_ingredient
 121 | Can add Категория ингредиента    |              31 | add_ingredientcategory
 122 | Can change Категория ингредиента |              31 | change_ingredientcategory
 123 | Can delete Категория ингредиента |              31 | delete_ingredientcategory
 124 | Can view Категория ингредиента   |              31 | view_ingredientcategory
 125 | Can add Инструмент               |              32 | add_tool
 126 | Can change Инструмент            |              32 | change_tool
 127 | Can delete Инструмент            |              32 | delete_tool
 128 | Can view Инструмент              |              32 | view_tool
 129 | Can add Рецепт                   |              33 | add_recipe
 130 | Can change Рецепт                |              33 | change_recipe
 131 | Can delete Рецепт                |              33 | delete_recipe
 132 | Can view Рецепт                  |              33 | view_recipe
 133 | Can add Товар                    |              34 | add_goods
 134 | Can change Товар                 |              34 | change_goods
 135 | Can delete Товар                 |              34 | delete_goods
 136 | Can view Товар                   |              34 | view_goods
 137 | Can add Избранный рецепт         |              35 | add_favoriterecipe
 138 | Can change Избранный рецепт      |              35 | change_favoriterecipe
 139 | Can delete Избранный рецепт      |              35 | delete_favoriterecipe
 140 | Can view Избранный рецепт        |              35 | view_favoriterecipe
 141 | Can add Инструмент               |              36 | add_tool
 142 | Can change Инструмент            |              36 | change_tool
 143 | Can delete Инструмент            |              36 | delete_tool
 144 | Can view Инструмент              |              36 | view_tool
 145 | Can add Рецепт                   |              37 | add_recipe
 146 | Can change Рецепт                |              37 | change_recipe
 147 | Can delete Рецепт                |              37 | delete_recipe
 148 | Can view Рецепт                  |              37 | view_recipe
 149 | Can add Категория ингредиента    |              38 | add_ingredientcategory
 150 | Can change Категория ингредиента |              38 | change_ingredientcategory
 151 | Can delete Категория ингредиента |              38 | delete_ingredientcategory
 152 | Can view Категория ингредиента   |              38 | view_ingredientcategory
 153 | Can add Ингредиент               |              39 | add_ingredient
 154 | Can change Ингредиент            |              39 | change_ingredient
 155 | Can delete Ингредиент            |              39 | delete_ingredient
 156 | Can view Ингредиент              |              39 | view_ingredient
 157 | Can add temp code                |              40 | add_tempcode
 158 | Can change temp code             |              40 | change_tempcode
 159 | Can delete temp code             |              40 | delete_tempcode
 160 | Can view temp code               |              40 | view_tempcode
 161 | Can add Ингредиент рецепта       |              41 | add_recipeingredient
 162 | Can change Ингредиент рецепта    |              41 | change_recipeingredient
 163 | Can delete Ингредиент рецепта    |              41 | delete_recipeingredient
 164 | Can view Ингредиент рецепта      |              41 | view_recipeingredient

"""


class TempCode(models.Model):
    email = models.EmailField(unique=True)
    verification_code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField('Подтвержден?', default=False)


class User(BaseModel, AbstractUser):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ]

    OS_CHOICES = [
        ('Android', 'Android'),
        ('IOS', 'IOS')
    ]

    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='150 символов или меньше. Может содержать только буквы, цифры и символы @/./+/-/_ .',
        validators=[UnicodeUsernameValidator()],
        error_messages=dict(unique='Пользователь с таким именем уже существует'),
        verbose_name='Username',
    )
    # todo: обязательное, но нужно его брать при авторизации через google и тд
    email = models.EmailField(max_length=150, null=True, blank=True, verbose_name='E-mail')
    phone = CharField(null=True, blank=True, default=None, db_index=True, verbose_name='Телефон')
    is_active = models.BooleanField('Активный?', default=True)

    first_name = models.CharField(max_length=150, default='', blank=True, db_index=True, verbose_name='Имя')
    last_name = models.CharField(max_length=150, default='', blank=True, db_index=True, verbose_name='Фамилия')

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        verbose_name='Пол',
        default='Other'
    )

    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    avatar = models.FileField(null=True, blank=True, upload_to='avatars/', verbose_name='Аватар')
    os = models.CharField(choices=OS_CHOICES, null=True, blank=True, default=None, verbose_name='Операционная система')

    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} ({self.email or self.phone})'

    @property
    @display(description='ФИ')
    def full_name(self) -> str:
        return f'{self.last_name or ""} {self.first_name or ""}'.strip()  # noqa

    def save(self, *args, **kwargs):
        if self.email and (self.username != self.email):
            self.username = self.email
        super().save(*args, **kwargs)


class ForgetRequest(BaseModel):
    user = ForeignKey(User, related_name='forget_requests')
    link = models.CharField(max_length=30, verbose_name='Код ссылки')
    enabled = models.BooleanField(default=True, verbose_name='Статус запроса')

    class Meta:
        verbose_name = 'Восстановление пароля'
        verbose_name_plural = 'Восстановление паролей'

    def __str__(self):
        return f'{self.link}: {self.enabled and "active" or "disabled"}'


class Referral(CreatedUpdatedModel):
    user = ForeignKey(User, related_name='referrals', verbose_name='Создатель кода')
    code = models.CharField(max_length=150, db_index=True, unique=True, verbose_name='Код')
    code_applying = models.IntegerField(default=0, verbose_name='Применений кода')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')

    class Meta:
        ordering = ['id']
        verbose_name = 'Реферальный код'
        verbose_name_plural = 'Реферальные коды'

    def __str__(self):
        return '{}'.format(self.code)


class Point(BaseModel):
    user = ForeignKey(User, related_name='points', verbose_name='Пользователь')
    text = models.CharField(max_length=150, null=True, blank=True, verbose_name='Текст')
    created_at = models.DateTimeField(default=timezone.now, blank=True, verbose_name='Создано')
    points = models.PositiveIntegerField(verbose_name='Баллы')
    charge = models.BooleanField(default=False, verbose_name='Списание?')

    class Meta:
        ordering = ['id']
        verbose_name = 'Балл'
        verbose_name_plural = 'Баллы'


class Notification(BaseModel):
    user = ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='notifications')
    topik = models.CharField(max_length=255, null=True, blank=True, verbose_name='Заголовок')
    topik_eng = models.CharField(max_length=255, null=True, blank=True, verbose_name='Заголовок на ENG')
    message = models.TextField(null=True, blank=True, verbose_name='Сообщение')
    message_eng = models.TextField(null=True, blank=True, verbose_name='Сообщение на ENG')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification: {self.message} for {self.user.email}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
import os

import django
from locust import HttpUser, task, between

from cocktails.api.v1.main.urls_handling import make_string_link

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_core.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from cocktails.apps.recipes.models import Quest, MemberStatusType


class StudentUser(HttpUser):
    wait_time = between(1, 2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quest: Quest = Quest.objects.filter(
            quest_members__isnull=False,
            quest_members__status=MemberStatusType.MEMBER,
        ).last()
        self.student_user = self.quest.quest_members.filter(status=MemberStatusType.MEMBER).last().user
        self.ses = make_string_link(self.quest.id)
        self.student_headers = {
            'Authorization': f'Token {self.student_user.auth_token.key}',
            'Organization-Subdomain': self.quest.organization.subdomain,
        }
        self.stage = self.quest.stages.last()

    @task(1)
    def index(self):
        self.client.get('https://main.cocktails.ru/')

    @task(1)
    def admin(self):
        self.client.get('/admin/')

    @task(1)
    def auth(self):
        self.client.post(
            '/api/v1/auth/web/sign-in/',
            json=dict(email='cocktails@mail.ru', password='12345678'),
            headers={'Organization-Subdomain': self.quest.organization.subdomain},
        )

    @task(3)
    def get_quest_list(self):
        self.client.get('/api/v1/student/recipes/recipes/', headers=self.student_headers)

    @task(3)
    def get_quest(self):
        self.client.get(f'/api/v1/student/recipes/recipes/{self.ses}/', headers=self.student_headers)

    @task(1)
    def get_quest_review(self):
        self.client.get('/api/v1/student/recipes/quest_review/', headers=self.student_headers)

    @task(1)
    def get_actual_quest(self):
        self.client.get('/api/v1/student/recipes/actual_quest/', headers=self.student_headers)

    @task(1)
    def get_stages(self):
        self.client.get(f'/api/request/get_stages?quest_id={self.quest.pk}', headers=self.student_headers)

    @task(3)
    def get_stage_theories_info(self):
        self.client.get(f'/api/request/get_stage_theories_info?stage_id={self.stage.pk}', headers=self.student_headers)

    @task(5)
    def get_config(self):
        self.client.get('/api/v1/common/config/')

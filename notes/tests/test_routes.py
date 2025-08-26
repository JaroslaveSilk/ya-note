from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):        
        cls.author = User.objects.create(username='Владелец')
        cls.other_user = User.objects.create(username='ДругойЮзер')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Содежание',
            slug='zagolovoklink',
            author=cls.author
            )

    def test_pages_availability(self):
        """Проверяет доступность страниц зарегистрированному
        пользователю и недоступность чужих заметок не
        автору этих заметок."""
        users = self.author, self.other_user
        urls = (
            ('notes:home', None),
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:list', None),
            ('notes:success', None),
            ('users:login', None),
            ('users:signup', None),
        )
        for user in users:
            self.client.force_login(user)
            for name, args in urls:
                expected_status = (HTTPStatus.NOT_FOUND
                                   if user == self.other_user and args
                                   else HTTPStatus.OK)
                with self.subTest(user=user, name=name):
                    response = self.client.get(reverse(name, args=args))
                    self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anon_client(self):
        """Проверка редиректов для анонима."""
        LOGIN_URL = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:list', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                redirect_url = f'{LOGIN_URL}?next={url}'
                self.assertRedirects(
                    response,
                    redirect_url
                )

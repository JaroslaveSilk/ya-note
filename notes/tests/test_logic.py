from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import WARNING

from notes.models import Note

from .test_routes import User


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст заметки для проверки'

    @classmethod
    def setUpTestData(cls):
        cls.authorized = User.objects.create(username='Авторизованный')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.authorized)
        cls.add_url = reverse('notes:add')
        cls.bad_slug_data = 'zagolovok'
        cls.form_data = {
            'title': 'Заголовок',
            'text': cls.NOTE_TEXT,
            'slug': cls.bad_slug_data,
        }
        cls.redirect_url = reverse('notes:success')

    def test_anon_user_cant_create_note(self):
        self.client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, f'{self.redirect_url}')
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.get().text, self.NOTE_TEXT)
        self.assertEqual(Note.objects.get().author, self.authorized)

    def test_user_cant_create_same_slug_notes(self):
        self.auth_client.post(self.add_url, data=self.form_data)
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            form=response.context['form'],
            field='slug',
            errors=self.bad_slug_data + WARNING
        )
        self.assertEqual(Note.objects.count(), 1)


class TestNotesEditDelete(TestCase):
    NEW_NOTE_TEXT = 'Новый текст'
    NOTE_TEXT = 'Текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.other_user = User.objects.create(username='Пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user_client = Client()
        cls.user_client.force_login(cls.other_user)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'text': cls.NEW_NOTE_TEXT,
            'title': cls.NEW_NOTE_TEXT,
        }
        cls.base_redirect = reverse('notes:success')

    def test_author_can_delete(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.base_redirect)
        self.assertEqual(Note.objects.count(), 0)

    def test_author_can_edit(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.base_redirect)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_non_author_cant_delete(self):
        response = self.user_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_non_author_cant_edit(self):
        response = self.user_client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(self.note.text, self.NOTE_TEXT)

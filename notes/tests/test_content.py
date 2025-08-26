from django.test import TestCase
from django.urls import reverse

from notes.models import Note

from .test_routes import User


class TestListPage(TestCase):
    LIST_URL = reverse('notes:list')
    NOTES_TEST_COUNT = 10

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        all_notes = [
            Note(
                title=f'Запись {counter}',
                text = 'Содержание записи',
                slug=f'Zapis{counter}',
                author=cls.author
            )
            for counter in range(cls.NOTES_TEST_COUNT + 1)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_order(self):
        """Проверка порядка отображения заметок."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        all_notes = [note.id for note in response.context['note_list']]
        sorted_notes = sorted(all_notes)
        self.assertEqual(all_notes, sorted_notes)

class TestAddPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.add_url = reverse('notes:add')

    def test_anon_has_no_form(self):
        self.assertNotIn('form', self.client.get(self.add_url))

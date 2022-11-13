from django.test import TestCase, Client


class TestURLAbout(TestCase):

    def setUp(self) -> None:
        self.client = Client()

    def test_about_url(self):
        """Тестируем соответствие шаблонов приложения about"""

        templates_url_name = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }

        for address, template in templates_url_name.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)

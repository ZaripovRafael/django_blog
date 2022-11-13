from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Group
from http import HTTPStatus


User = get_user_model()


class PostURLTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='TestAuthor')
        cls.not_author = User.objects.create(username='TestNotAuthor')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group
        )
        cls.PUBLIC_URLS: dict = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.not_author.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
        }

        cls.PRIVATE_URLS:dict = {
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_not_author = Client()
        
        self.authorized_client_author.force_login(PostURLTest.author)
        self.authorized_client_not_author.force_login(PostURLTest.not_author)

    def test_guest_users_public_correct_template(self):
        """Проверяем доступность публичных адресов гостевой учеткой"""

        for address, template in PostURLTest.PUBLIC_URLS.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_guest_users_private_correct_template(self):
        """Проверяем недоступность приватных адресов гостевой учеткой"""
        post_pk = PostURLTest.post.pk
        for address, template in PostURLTest.PRIVATE_URLS.items():
            response = self.guest_client.get(address, follow=True)
            if address == f'/posts/{post_pk}/edit/':
                self.assertRedirects(
                            response,
                            '/auth/login/?next=/posts/1/edit/',
                            status_code=HTTPStatus.FOUND,
                            target_status_code=HTTPStatus.OK
                        )
            else:
                self.assertRedirects(
                    response,
                    '/auth/login/?next=/create/',
                    status_code=HTTPStatus.FOUND,
                    target_status_code=HTTPStatus.OK
                )

    def test_auth_user_public_correct_template(self):

        for address, template in PostURLTest.PUBLIC_URLS.items():
            with self.subTest(address=address):
                response = self.authorized_client_not_author.get(
                    address
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_404_for_unexisting_page(self):
        """Проверка 404 ошибки при обращении к несуществующей странице"""

        address = '/page_not_found/'

        guest = self.guest_client.get(address, follow=True)
        author = self.authorized_client_author.get(address)
        # так как успел сделать кастомную 404 страницу статус код должен быть 200
        self.assertEqual(guest.status_code, HTTPStatus.OK)
        self.assertEqual(author.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(guest, 'core/404.html')
        self.assertTemplateUsed(author, 'core/404.html')


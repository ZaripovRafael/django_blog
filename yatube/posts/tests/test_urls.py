from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Group


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
        

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_not_author = Client()
        
        self.authorized_client_author.force_login(PostURLTest.author)
        self.authorized_client_not_author.force_login(PostURLTest.not_author)

    def test_users_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        group = PostURLTest.group
        user = PostURLTest.author
        post = PostURLTest.post

        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/profile/{user.username}/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
            f'/posts/{post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_404_for_unexisting_page(self):
        """Проверка 404 ошибки при обращении к несуществующей странице"""

        address = '/unexisting_page/'

        guest = self.guest_client.get(address, follow=True)
        author = self.authorized_client_author.get(address)

        self.assertEqual(guest.reason_phrase, 'Not Found')
        self.assertEqual(author.reason_phrase, 'Not Found')
    
    def test_create_post(self):
        """Проверка на создание поста"""

        address = '/create/'

        guest_response = self.guest_client.get(address, follow=True)
        not_author_response = self.authorized_client_not_author.get(address)
        author_response = self.authorized_client_author.get(address)

        self.assertRedirects(guest_response, '/auth/login/?next=/create/')
        self.assertEqual(not_author_response.reason_phrase, 'OK')
        self.assertEqual(author_response.reason_phrase, 'OK')

    def test_edit_post(self):

        post_pk = PostURLTest.post.pk
        address = f'/posts/{post_pk}/edit'

        guest_response = self.guest_client.get(address, follow=True)
        not_author_response = self.authorized_client_not_author.get(address, follow=True)
        author_response = self.authorized_client_author.get(address)

        self.assertRedirects(
            guest_response,
            f'/auth/login/?next=/posts/{post_pk}/edit/',
            status_code=301,
            target_status_code=200
            )
        self.assertRedirects(not_author_response, f'/posts/{post_pk}/', status_code=301, target_status_code=200)
        self.assertEqual(author_response.url, f'/posts/{post_pk}/edit/')

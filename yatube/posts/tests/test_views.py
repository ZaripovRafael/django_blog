from urllib import response
from django import forms
from django.test import Client, TestCase
from django.urls import reverse


from posts.models import Post, Group, User


INDEX = reverse('posts:index')
SLUG = 'test-slug'
GROUP = reverse('posts:groups', kwargs={'slug': SLUG})
ANOTHER_SLUG = 'another-test-slug'
USERNAME = 'TestUser'
PROFILE = reverse('posts:profile', kwargs={'username': USERNAME})
POSTS = 15

class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        cls.another_group = Group.objects.create(
            title='Другая группа',
            slug='AnotherGroup',
            description='Проверочная группа'
        )
        cls.user = User.objects.create(username='TestUser')

        for _ in range(14):
            Post.objects.create(
                text='Тестовый текст',
                author=cls.user,
                group=cls.group,
            )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self) -> None:
        self.guest = Client()
        self.author = Client()
        self.author.force_login(PostsPagesTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        template_pages_names = {
            'posts/index.html': INDEX,
            'posts/group_list.html': GROUP,
            'posts/profile.html': PROFILE,
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsPagesTests.post.pk}
                ),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/create_post.html': reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsPagesTests.post.pk}
                )
        }

        for template, reverse_name in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author.get(reverse_name)
                self.assertTemplateUsed(response, template)
    
    def test_pages_show_correct_context(self):
        list_of_pages = [INDEX, GROUP, PROFILE]
        for page in list_of_pages:
            response = self.author.get(page)
            post_object = response.context['page_obj'][0]
            post_text = post_object.text
            post_author = post_object.author.username
            post_group = post_object.group.title
            self.assertEqual(
                post_text,
                'Тестовый текст',
                f'сраница {page} содержит неправильный текст')
            self.assertEqual(
                post_author,
                'TestUser',
                f'пост на сранице {page} содержит неправильного автора')
            self.assertEqual(
                post_group,
                'Тестовая группа',
                f'сраница {page} содержит неправильную группу')

    def test_post_detail_show_correct_context(self):
        response = self.author.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostsPagesTests.post.pk}))
        post = response.context['post']
        post_number = response.context['number_of_post']
        self.assertEqual(post.text, 'Тестовый текст')
        self.assertEqual(post.group.title, 'Тестовая группа')
        self.assertEqual(post.author.username, 'TestUser')
        self.assertEqual(post_number, 15)

    def post_create_show_correct_context(self):
        """Проверка post_create имеет правильную форму"""
        response = self.author.get(reverse('posts:post_create'))
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
    
    def post_edit_show_correct_context(self):
        """страница post_edit сформирован с правильным контекстом"""
        response = self.author.get(reverse('posts:post_edit'))
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        form_values = {
            'text': 'Тест',
            'group': 1,
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                text_field = response.context.get('form').initial[value]
                self.assertIsInstance(form_field, expected)

                self.assertEqual(text_field, form_values[value])

                self.assertTrue(response.context['is_edit'])

    def test_first_page_contains_ten_records(self):
        reverse_names = [INDEX, GROUP, PROFILE]
        for name in reverse_names:
            with self.subTest(reverse_name=name):
                response = self.author.get(name)
                self.assertEqual(
                    len(response.context['page_obj']), 10
                )
    def test_second_page_contains_five_records(self):
        reverse_names = [
            INDEX + '?page=2',
            GROUP + '?page=2',
            PROFILE + '?page=2'
            ]
        for name in reverse_names:
            with self.subTest(reverse_name=name):
                response = self.author.get(name)
                self.assertEqual(
                    len(response.context['page_obj']), 5
                )

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.user = User.objects.create(username='TestUser')

    def setUp(self) -> None:
        self.client = Client()
        self.client.force_login(PostCreateFormTest.user)
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=PostCreateFormTest.user,
            group=PostCreateFormTest.group
        )

    def test_create_post(self):
        form_data = {
            'text': 'Test text',
            'group': PostCreateFormTest.group.pk
        }

        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        pos_obj = response.context['page_obj'][0]
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(pos_obj.text, form_data['text'])
        self.assertEqual(pos_obj.group, PostCreateFormTest.group)
        self.assertEqual(pos_obj.author, PostCreateFormTest.user)
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs=({'username': PostCreateFormTest.user.username}
                )
            )
        )

    def test_post_edit_save(self):
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.pk,
        }
        response = self.client.post(
            reverse(
                'posts:post_edit',
                args=[self.post.pk]),
            data=form_data,
            follow=True
        )
        post = response.context['post']
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.post.author)
        self.assertRedirects(response, f'/posts/{self.post.pk}/')


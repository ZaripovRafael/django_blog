from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group
from ..forms import PostForm


User = get_user_model()


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
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=PostCreateFormTest.user,
            group=PostCreateFormTest.group
        )

    def setUp(self) -> None:
        self.client = Client()
        self.client.force_login(PostCreateFormTest.user)

    def test_create_post(self):
        post_count = Post.objects.count()

        form_data = {
            'text': 'Test text',
            'group': PostCreateFormTest.group.pk
        }
        form = PostForm(form_data)
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group,
                author=self.user,
            ).exists()
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs=({'username': PostCreateFormTest.user.username})
            )
        )

    def test_post_edit_save(self):
        posts_count = Post.objects.count()
        post_pk = self.post.pk
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.pk
        }
        self.client.post(
            reverse('posts:post_edit', kwargs=({'post_id': post_pk})),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(
            Post.objects.get(pk=post_pk).text,
            form_data['text']
        )
        self.assertTrue(
            Post.objects.filter(
                pk=post_pk,
                text=form_data['text']
            ).exists()
        )

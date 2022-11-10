from django.contrib.auth import get_user_model
from django.test import TestCase
from pytils.translit import translify

from ..models import Group, Post


User = get_user_model()


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __sts__"""

        post_str = PostModelTest.post.__str__()
        group_str = PostModelTest.group.__str__()

        max_length_post_str = 15
        self.assertLessEqual(
            len(post_str),
            max_length_post_str,
            'Длина object_name модели Post больше 15'
        )
        self.assertEqual(
            translify(group_str),
            translify('Тестовая группа'),
            'Неправильный object_name для модели Group'
        )

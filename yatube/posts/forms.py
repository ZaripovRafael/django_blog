from django import forms
from .models import Post


class PostForm(forms.ModelForm):

    class Meta:

        model = Post
        fields = ('text', 'group', 'image')

    def empty_text(self):
        data = self.cleaned_data['text']

        if self.cleaned_data['text'] == '':
            raise forms.ValidationError('Пост не может быть пустым')
        return data

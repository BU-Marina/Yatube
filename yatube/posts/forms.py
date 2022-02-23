from django.forms import ModelForm, ValidationError
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        data = self.cleaned_data['text']
        if not data:
            raise ValidationError('Поле текста должно быть заполнено')
        return data


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        data = self.cleaned_data['text']
        if not data:
            raise ValidationError('Поле текста должно быть заполнено')
        return data

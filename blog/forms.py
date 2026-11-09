
from django import forms
from django.contrib.auth.hashers import make_password
from .models import Article, Comment, User, Role, Author


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['user', 'comment_text']
        labels = {
            'user': 'Ваше имя пользователя',
            'comment_text': 'Текст комментария',
        }
        widgets = {
            'comment_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Напишите свой комментарий...'
            }),
            'user': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['user'].queryset = User.objects.filter(
            role__role_name='Читатель',
            is_active=True
        )

        self.fields['user'].empty_label = 'Выберите автора...'


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )
    password_confirm = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
        }
        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'form-control'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error(
                'password_confirm',
                'Пароли не совпадают.'
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.password_hash = make_password(
            self.cleaned_data['password']
        )
        user.role = Role.objects.get(role_name='Читатель')

        if commit:
            user.save()

        return user


class ArticleForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=[
            ('Черновик', 'Черновик'),
            ('Отправить на проверку', 'Отправить на проверку'),
        ],
        label='Действие',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Article
        fields = [
            'title',
            'short_description',
            'content',
            'author',
            'category',
            'status',
            'tags',
        ]

        labels = {
            'title': 'Заголовок',
            'short_description': 'Краткое описание',
            'content': 'Текст публикации',
            'author': 'Автор',
            'category': 'Категория',
            'status': 'Статус',
            'tags': 'Теги',
        }

        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'short_description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'content': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 10}
            ),
            'author': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'category': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'status': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)




class LoginForm(forms.Form):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )

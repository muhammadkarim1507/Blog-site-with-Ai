from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Post, Comment, Category


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post
        fields = ['title', 'category', 'excerpt', 'content', 'cover_image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ajoyib sarlavha kiriting...',
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Qisqa tavsif (ixtiyoriy — bo\'sh qolsa avtomatik olinadi)',
            }),
            'category': forms.Select(attrs={
                'class': 'form-input',
            }),
            'status': forms.Select(attrs={
                'class': 'form-input',
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Kategoriya tanlang (ixtiyoriy)"
        self.fields['category'].required = False
        self.fields['cover_image'].required = False
        self.fields['excerpt'].required = False

        # Label'larni o'zbekchalashtirish
        self.fields['title'].label = "Sarlavha"
        self.fields['category'].label = "Kategoriya"
        self.fields['excerpt'].label = "Qisqa tavsif"
        self.fields['content'].label = "Kontent"
        self.fields['cover_image'].label = "Muqova rasmi"
        self.fields['status'].label = "Holat"


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'comment-input',
                'rows': 3,
                'placeholder': 'Fikringizni yozing...',
            }),
        }
        labels = {
            'text': '',
        }


class ReplyForm(forms.ModelForm):
    """Reply uchun alohida forma"""
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'comment-input reply-input',
                'rows': 2,
                'placeholder': 'Javobingizni yozing...',
            }),
        }
        labels = {
            'text': '',
        }
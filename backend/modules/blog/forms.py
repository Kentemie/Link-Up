from django import forms

from .models import Article, Comment



class ArticleCreateForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ('title', 'slug', 'category', 'short_description', 'full_description', 'thumbnail', 'status')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off',
            })

        self.fields['short_description'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})
        self.fields['full_description'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})
        self.fields['short_description'].required = False
        self.fields['full_description'].required = False



class ArticleUpdateForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ArticleCreateForm.Meta.fields + ('the_one_who_updated', 'fixed')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off',
            })

        self.fields['fixed'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['short_description'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})
        self.fields['full_description'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})
        self.fields['short_description'].required = False
        self.fields['full_description'].required = False



class CommentCreateForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('content',)

    parent = forms.IntegerField(
        widget=forms.HiddenInput, 
        required=False
    )
    content = forms.CharField(
        label='', 
        widget=forms.Textarea(
            attrs={
                'cols': 30, 
                'rows': 5, 
                'placeholder': 'Comment', 
                'class': 'form-control'
            }
        )
    )

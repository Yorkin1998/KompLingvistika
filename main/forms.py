from django import forms

class TextAnalyzeForm(forms.Form):
    text = forms.CharField(
        label="Matn kiriting",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Bu yerga matn kiriting...',
            'rows': 4
        })
    )
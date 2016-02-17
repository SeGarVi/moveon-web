from django import forms 
 
#Not used yet

class login(forms.Form): 
     user = forms.CharField(
     	max_length=100, 
     	widget=forms.TextInput({ "placeholder": "Your subject"})) 
     email = forms.EmailField(
     	widget=forms.TextInput({ "placeholder": "your@email.com"})) 
     message = forms.CharField(
     	widget=forms.Textarea)

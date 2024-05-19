from django import forms
from .models import Company
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class QueryForm(forms.Form):
    keyword = forms.CharField(required=False, label='Keyword', widget=forms.TextInput(attrs={'class': 'form-control'}))
    industry = forms.ChoiceField(required=False, label='Industry', widget=forms.Select(attrs={'class': 'form-control'}))
    year_founded = forms.ChoiceField(required=False, label='Year Founded', widget=forms.Select(attrs={'class': 'form-control'}))
    city = forms.ChoiceField(required=False, label='City', widget=forms.Select(attrs={'class': 'form-control'}))
    state = forms.ChoiceField(required=False, label='State', widget=forms.Select(attrs={'class': 'form-control'}))
    country = forms.ChoiceField(required=False, label='Country', widget=forms.Select(attrs={'class': 'form-control'}))
    employees_from = forms.ChoiceField(required=False, label='Employees (From)', widget=forms.Select(attrs={'class': 'form-control'}))
    employees_to = forms.ChoiceField(required=False, label='Employees (To)', widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(QueryForm, self).__init__(*args, **kwargs)
        
        self.fields['industry'].choices = self.get_unique_choices('industry')
        self.fields['year_founded'].choices = self.get_unique_choices('year_founded')
        self.fields['city'].choices = self.get_unique_choices('city')
        self.fields['state'].choices = self.get_unique_choices('state')
        self.fields['country'].choices = self.get_unique_choices('country')
        self.fields['employees_from'].choices = self.get_employee_choices('current_employee_estimate')
        self.fields['employees_to'].choices = self.get_employee_choices('current_employee_estimate')

    def get_unique_choices(self, field_name):
        if field_name == 'year_founded':
            choices = Company.objects.order_by('-year_founded').values_list(field_name, flat=True).distinct()
        else:
            choices = Company.objects.values_list(field_name, flat=True).distinct()
        return [('', f'Select {field_name.capitalize()}')] + [(choice, choice) for choice in choices]

    def get_employee_choices(self, field_name):
        choices = Company.objects.values_list(field_name, flat=True).distinct()
        return [('', 'Select Number of Employees')] + [(choice, choice) for choice in sorted(choices)]
    

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


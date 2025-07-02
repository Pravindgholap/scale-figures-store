from django import forms
from .models import Order

# Form for creating a new order during checkout
class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'mt-1 block w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 text-lg'}),
            'last_name': forms.TextInput(attrs={'class': 'mt-1 block w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 text-lg'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 text-lg'}),
            'address': forms.TextInput(attrs={'class': 'mt-1 block w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 text-lg'}),
            'postal_code': forms.TextInput(attrs={'class': 'mt-1 block w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 text-lg'}),
            'city': forms.TextInput(attrs={'class': 'mt-1 block w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 text-lg'}),
        }

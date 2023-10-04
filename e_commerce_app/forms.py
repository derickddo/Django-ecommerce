from django import forms

class CheckoutForm(forms.Form):

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control'}),
        required=True 
    )
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),
        required=True,
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={'id':'email-address', 'class':'form-control'}),required=True)
    
    phone_number= forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=True,
    )
    
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address', 'class':'form-control'}),
        required=True 
    )
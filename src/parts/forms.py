from django import forms


class UploadCSVFileForm(forms.Form):
    csv_file = forms.FileField()

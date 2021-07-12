from django.contrib import admin
from django.forms import ModelForm

from apps.user.models import CustomUser, CustomSetting


class CustomUserCreationForm(ModelForm):

    class Meta:
        model = CustomUser
        fields = "__all__"
        exclude = ['groups', 'user_permissions', 'last_login']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': True})

    def save(self, commit=True):
        user = super().save(commit=False)
        if 'pbkdf2_sha256' not in user.password:
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserCreationForm
    list_display = ['username', 'fullname', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'fullname']


class CustomSettingAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'value'
    ]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CustomSetting, CustomSettingAdmin)

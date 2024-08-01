import os
from django.utils.html import format_html
from django.contrib import admin
from MedProject.settings import BASE_DIR, BASE_URL
from .models import FieldOfActivity, User, UserApprovalApplication, UserEditApplication, FoAUserConnection
from django.db.models.fields.reverse_related import ManyToOneRel
from django_summernote.admin import SummernoteModelAdmin


@admin.register(FieldOfActivity)
class FieldOfActivityAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FieldOfActivity._meta.get_fields() if type(field) != ManyToOneRel]


@admin.register(User)
class UserAdmin(SummernoteModelAdmin):
    list_display = ['id', 'username', 'last_login', 'first_name', 'patronymic', 'last_name', 'order', 'birthdate',
                    'fields_of_activity', 'profession', 'city', 'workplace_address', 'workplace_name',
                    'phone_number', 'email', 'photo', 'short_description', 'email_verified']
    exclude = ('groups', 'is_superuser', 'is_staff', 'user_permissions', 'password', 'verification_key',
               'verification_key_expires')

    list_display_links = ('id', 'username', 'first_name', 'patronymic', 'last_name')
    summernote_fields = ('description',)

    def short_description(self, obj):
        return obj.description[:50] + '...'

    short_description.short_description = 'О себе'

    def fields_of_activity(self, obj):
        return obj.fields_of_activity

    fields_of_activity.short_description = 'Сферы деятельности'

    def save_model(self, request, obj, form, change):
        if not change or (change and 'photo' in form.changed_data):
            if change:
                try:
                    os.remove(os.path.join(BASE_DIR, 'media', form.initial['photo'].name))
                except (FileNotFoundError, UnicodeEncodeError):
                    pass
            # compress_img(form.instance, 'photo', 'profile_photos')
        if (not change or (change and 'approved' in form.changed_data)) and form.instance.approved:
            app = UserApprovalApplication.objects.filter(user__pk=form.instance.pk, response=False)
            if app.exists():
                app = app.last()
                app.treated = True
                app.response = True
                app.save()
        return super(UserAdmin, self).save_model(request, obj, form, change)


@admin.register(UserApprovalApplication)
class UserApprovalApplicationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserApprovalApplication._meta.get_fields()]


@admin.register(UserEditApplication)
class UserEditApplicationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserEditApplication._meta.get_fields()]
    exclude = ('field', 'new_value', 'old_value')
    readonly_fields = ['user', 'verbose_field', 'old_value_changed', 'new_value_changed']
    fields = ['user', 'verbose_field', 'old_value_changed', 'new_value_changed', 'treated', 'response', 'comment']

    def new_value_changed(self, obj):
        if obj.field == 'photo':
            url = f'{BASE_URL}/media/{obj.new_value}'
            return format_html(f"<img src='{url}' style='max-width: 300px; max-height: 300px;'>")
        else:
            return obj.get_value

    def old_value_changed(self, obj):
        if obj.field == 'photo':
            url = f'{BASE_URL}/media/{obj.old_value}'
            return format_html(f"<img src='{url}' style='max-width: 300px; max-height: 300px;'>")
        else:
            return obj.old_value

    old_value_changed.short_description = 'Старое значение'
    new_value_changed.short_description = 'Новое значение'


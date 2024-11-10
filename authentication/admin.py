import os
from django.utils.html import format_html
from django.contrib import admin
from MedProject.settings import BASE_DIR, BASE_URL
from .models import FieldOfActivity, User, UserApprovalApplication, UserEditApplication, FoAUserConnection
from django.db.models.fields.reverse_related import ManyToOneRel
from django_summernote.admin import SummernoteModelAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from anketa.models import CustomCRMUser





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

    def get_queryset(self, request):
        # Получаем базовый QuerySet
        qs = super().get_queryset(request)
        # Исключаем пользователей, которые являются экземплярами модели CustomCRMUser
        return qs.exclude(pk__in=CustomCRMUser.objects.values_list('pk', flat=True))


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
# @admin.register(User)
# class CustomUserAdmin(DefaultUserAdmin, SummernoteModelAdmin):
#     form = UserChangeForm

#     list_display = [
#         'id', 'username', 'last_login', 'first_name', 'patronymic', 'last_name', 'order', 'birthdate',
#         'fields_of_activity', 'profession', 'city', 'workplace_address', 'workplace_name', 'phone_number',
#         'email', 'photo', 'short_description', 'email_verified', 'is_staff', 'is_superuser', 'approved', 'display_groups'
#     ]
#     list_display_links = ('id', 'username', 'first_name', 'patronymic', 'last_name')
#     summernote_fields = ('description',)
#     list_filter = ('is_staff', 'is_superuser', 'approved', 'email_verified', 'groups')
#     search_fields = ('username', 'first_name', 'last_name', 'email')

#     readonly_fields = ('last_login',)

#     fieldsets = (
#         (None, {'fields': ('username', 'password', 'email', 'email_verified')}),
#         ('Personal info', {'fields': ('first_name', 'patronymic', 'last_name', 'birthdate', 'photo', 'description')}),
#         ('Work info', {'fields': ('profession', 'city', 'workplace_address', 'workplace_name', 'phone_number')}),
#         ('Permissions', {'fields': ('is_staff', 'is_superuser', 'approved', 'groups')}),
#         ('Important dates', {'fields': ('last_login',)}),
#     )

#     actions = ['make_staff', 'revoke_staff', 'add_to_group', 'remove_from_group']

#     # Метод для отображения групп пользователя
#     def display_groups(self, obj):
#         return ', '.join([group.name for group in obj.groups.all()])
#     display_groups.short_description = 'Groups'

#     def make_staff(self, request, queryset):
#         limited_group, created = Group.objects.get_or_create(name="Limited Admin Access")
#         permissions = Permission.objects.filter(codename__in=['add_user', 'change_user', 'delete_user'])
#         limited_group.permissions.set(permissions)
#         queryset.update(is_staff=True)
#         for user in queryset:
#             user.groups.add(limited_group)
#     make_staff.short_description = 'Предоставить доступ к админ-панели с ограниченными правами'

#     def revoke_staff(self, request, queryset):
#         limited_group = Group.objects.get(name="Limited Admin Access")
#         queryset.update(is_staff=False)
#         for user in queryset:
#             user.groups.remove(limited_group)
#     revoke_staff.short_description = 'Удалить доступ к админ-панели'

#     def add_to_group(self, request, queryset):
#         # Пример добавления в группу "Limited Admin Access"
#         group, created = Group.objects.get_or_create(name="Limited Admin Access")
#         for user in queryset:
#             user.groups.add(group)
#     add_to_group.short_description = 'Добавить в группу "Limited Admin Access"'

#     def remove_from_group(self, request, queryset):
#         # Пример удаления из группы "Limited Admin Access"
#         group = Group.objects.get(name="Limited Admin Access")
#         for user in queryset:
#             user.groups.remove(group)
#     remove_from_group.short_description = 'Удалить из группы "Limited Admin Access"'

#     def short_description(self, obj):
#         return obj.description[:50] + '...'

#     short_description.short_description = 'О себе'

#     def fields_of_activity(self, obj):
#         return obj.fields_of_activity

#     fields_of_activity.short_description = 'Сферы деятельности'

#     def save_model(self, request, obj, form, change):
#         if not change or (change and 'photo' in form.changed_data):
#             if change:
#                 try:
#                     os.remove(os.path.join(BASE_DIR, 'media', form.initial['photo'].name))
#                 except (FileNotFoundError, UnicodeEncodeError):
#                     pass
#             # compress_img(form.instance, 'photo', 'profile_photos')
#         if (not change or (change and 'approved' in form.changed_data)) and form.instance.approved:
#             app = UserApprovalApplication.objects.filter(user__pk=form.instance.pk, response=False)
#             if app.exists():
#                 app = app.last()
#                 app.treated = True
#                 app.response = True
#                 app.save()
#         return super(UserAdmin, self).save_model(request, obj, form, change)


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


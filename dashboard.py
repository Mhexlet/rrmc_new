"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'MedProject.dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'MedProject.dashboard.CustomAppIndexDashboard'
"""

try:
    from django.urls import reverse
    from django.utils.translation import gettext_lazy as _
except ImportError:
    from django.core.urlresolvers import reverse
    from django.utils.translation import ugettext_lazy as _
from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from authentication.models import UserApprovalApplication, UserEditApplication
from specialists.models import ArticleApprovalApplication
from main.models import QuestionAnswer, Application, Review


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for MedProject.
    """
    def init_with_context(self, context):

        uaa_length = len(UserApprovalApplication.objects.filter(treated=False))
        uea_length = len(UserEditApplication.objects.filter(treated=False))
        aaa_length = len(ArticleApprovalApplication.objects.filter(treated=False))
        qa_length = len(QuestionAnswer.objects.filter(treated=False))
        review_length = len(Review.objects.filter(treated=False))
        application_length = len(Application.objects.filter(treated=False))

        self.children.append(modules.LinkList(
            _('Уведомления'),
            draggable=False,
            deletable=False,
            collapsible=False,
            children=[
                {
                    'title': f'Заявки на одобрение профиля: {uaa_length}',
                    'url': '/admin/authentication/userapprovalapplication/',
                    'attrs': {
                        'style': 'color: red;' if uaa_length else ''
                    }
                },
                {
                    'title': f'Заявки на изменение профиля: {uea_length}',
                    'url': '/admin/authentication/usereditapplication/',
                    'attrs': {
                        'style': 'color: red;' if uea_length else ''
                    }
                },
                {
                    'title': f'Заявки на одобрение статьи: {aaa_length}',
                    'url': '/admin/specialists/articleapprovalapplication/',
                    'attrs': {
                        'style': 'color: red;' if aaa_length else ''
                    }
                },
                {
                    'title': f'Вопросы: {qa_length}',
                    'url': '/admin/main/questionanswer/',
                    'attrs': {
                        'style': 'color: red;' if qa_length else ''
                    }
                },
                {
                    'title': f'Отзывы: {review_length}',
                    'url': '/admin/main/review/',
                    'attrs': {
                        'style': 'color: red;' if review_length else ''
                    }
                },
                {
                    'title': f'Заявки на консультацию: {application_length}',
                    'url': '/admin/main/application/',
                    'attrs': {
                        'style': 'color: red;' if application_length else ''
                    }
                },
            ]
        ))

        self.children.append(modules.LinkList(
            _('Альбомы и наборы файлов'),
            layout='inline',
            draggable=False,
            deletable=False,
            collapsible=False,
            children=[
                {'title': 'Добавить альбом', 'url': reverse('custom:add_album_page'), 'attrs': {'target': '_blank'}},
                {'title': 'Добавить набор файлов', 'url': reverse('custom:add_fileset_page'), 'attrs': {'target': '_blank'}},
            ]
        ))

        self.children.append(modules.AppList(
            _('Applications'),
            exclude=('django.contrib.*',),
        ))

        self.children.append(modules.AppList(
            _('Administration'),
            models=('django.contrib.*',),
        ))

        self.children.append(modules.RecentActions(_('Recent Actions'), 5))


class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for MedProject.
    """

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(self.app_title, self.models),
            modules.RecentActions(
                _('Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=5
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboard, self).init_with_context(context)

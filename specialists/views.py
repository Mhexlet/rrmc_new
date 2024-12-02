import calendar
import time
from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView
from authentication.models import User, FieldOfActivity
from main.models import SiteContent
from .models import Article, ArticleFile, ArticleApprovalApplication
from custom.models import Section, Page
from django.db.models import Q


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from .models import User, FieldOfActivity
from authentication.serializers import SpecialistSerializer, FieldOfActivitySerializer


@login_required
def account(request):

    not_treated = ArticleApprovalApplication.objects.filter(article__author__pk=request.user.pk, treated=False)
    rejected = ArticleApprovalApplication.objects.filter(article__author__pk=request.user.pk, treated=True, response=False)

    context = {
        'title': 'Личный кабинет',
        'not_treated': not_treated,
        'rejected': rejected,
        'header_content': [SiteContent.objects.get(name='email').content,
                                     SiteContent.objects.get(name='phone').content,
                                     SiteContent.objects.get(name='phone').content.translate(
                                         str.maketrans({' ': '', '-': '', '(': '', ')': ''}))],
    }

    return render(request, 'specialists/account.html', context)


def profile(request, pk):

    specialist = User.objects.get(pk=pk)

    context = {
        'title': f'{specialist}',
        'specialist': specialist,
        'menu_sections': Section.objects.all().order_by('order'),
        'account_section_id': int(SiteContent.objects.get(name='account_section_id').content),
        'menu_pages': Page.objects.filter(section=None),
        'header_content': [SiteContent.objects.get(name='email').content,
                                     SiteContent.objects.get(name='phone').content,
                                     SiteContent.objects.get(name='phone').content.translate(
                                         str.maketrans({' ': '', '-': '', '(': '', ')': ''}))]
    }

    return render(request, 'specialists/profile.html', context)


def article(request, pk):

    art = Article.objects.get(pk=pk)

    context = {
        'title': f'{art}',
        'article': art,
        'files': len(art.get_files) > 0,
        'menu_sections': Section.objects.all().order_by('order'),
        'account_section_id': int(SiteContent.objects.get(name='account_section_id').content),
        'menu_pages': Page.objects.filter(section=None),
        'header_content': [SiteContent.objects.get(name='email').content,
                                     SiteContent.objects.get(name='phone').content,
                                     SiteContent.objects.get(name='phone').content.translate(
                                         str.maketrans({' ': '', '-': '', '(': '', ')': ''}))]
    }

    return render(request, 'specialists/article.html', context)


class SpecialistsList(ListView):
    model = User
    template_name = 'specialists/specialists.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Специалисты ранней помощи',
        context['menu_sections'] = Section.objects.all().order_by('order')
        context['account_section_id'] = int(SiteContent.objects.get(name='account_section_id').content)
        context['menu_pages'] = Page.objects.filter(section=None)
        context['header_content'] = [SiteContent.objects.get(name='email').content,
                                     SiteContent.objects.get(name='phone').content,
                                     SiteContent.objects.get(name='phone').content.translate(
                                         str.maketrans({' ': '', '-': '', '(': '', ')': ''}))]

        return context

    def get_queryset(self):
        return User.objects.filter(is_superuser=False, approved=True).order_by('order')

# views.py

class SpecialistListView(APIView):
    def get(self, request):
        field_of_activity_id = request.GET.get('field_of_activity')

        # Фильтруем пользователей, исключая CustomCRMUser
        specialists = User.objects.filter(
            is_superuser=False,
            approved=True
        ).exclude(
            Q(customcrmuser__isnull=False)
        )

        if field_of_activity_id:
            specialists = specialists.filter(fields__foa_id=field_of_activity_id)

        specialists = specialists.order_by('order')
        serializer = SpecialistSerializer(specialists, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
# class SpecialistListView(APIView):
#     def get(self, request):
#         field_of_activity_id = request.GET.get('field_of_activity')
#         specialists = User.objects.filter(is_superuser=False, approved=True)

#         if field_of_activity_id:
#             specialists = specialists.filter(fields__foa_id=field_of_activity_id)

#         specialists = specialists.order_by('order')
#         serializer = SpecialistSerializer(specialists, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
class FieldOfActivityListView(APIView):
    def get(self, request):
        fields_of_activity = FieldOfActivity.objects.all()
        serializer = FieldOfActivitySerializer(fields_of_activity, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@login_required
def create_article_page(request):

    context = {
        'title': 'Новый материал',
        'header_content': [SiteContent.objects.get(name='phone').content, SiteContent.objects.get(name='email').content]
    }

    return render(request, 'specialists/create_article_page.html', context)


@login_required
def create_article(request):
    theme = request.POST.get('theme')
    title = request.POST.get('title')
    text = request.POST.get('text')

    if request.recaptcha_is_valid:
        if theme and title and text:
            try:
                art = Article.objects.create(author=request.user, theme=theme, title=title, text=text)
                ArticleApprovalApplication.objects.create(article=art)
                for pk_name, file in request.FILES.items():
                    name = pk_name[pk_name.index('-') + 1:]
                    current_gmt = time.gmtime()
                    time_stamp = calendar.timegm(current_gmt)
                    file.name = f'{time_stamp}-{uuid4().hex}.{file.name.split(".")[-1]}'
                    ArticleFile.objects.create(file=file, article=art, name=name)
                return JsonResponse({'result': 'ok'})
            except:
                pass
    else:
        return JsonResponse({'result': 'captcha'})

    return JsonResponse({'result': 'failed'})


@login_required
def edit_article_page(request, pk):

    art = Article.objects.get(pk=pk)

    context = {
        'title': 'Редактирование материала',
        'article': art if not art.approved else None,
        'header_content': [SiteContent.objects.get(name='email').content,
                                     SiteContent.objects.get(name='phone').content,
                                     SiteContent.objects.get(name='phone').content.translate(
                                         str.maketrans({' ': '', '-': '', '(': '', ')': ''}))],
        'files_quantity': len(art.get_files)
    }

    return render(request, 'specialists/edit_article_page.html', context)


@login_required
def edit_article(request):

    pk = int(request.POST.get('pk'))
    theme = request.POST.get('theme')
    title = request.POST.get('title')
    text = request.POST.get('text')
    kept_files = [int(i) for i in request.POST.get('kept_files').split(',') if i] if request.POST.get('kept_files') else []

    if request.recaptcha_is_valid:
        art = Article.objects.get(pk=pk)
        if not art.approved:
            try:
                art.theme = theme
                art.title = title
                art.text = text
                art.save()
                current_files = art.get_files
                for file in current_files:
                    if file.pk not in kept_files:
                        ArticleFile.objects.get(pk=file.pk).delete()
                for pk_name, file in request.FILES.items():
                    name = pk_name[pk_name.index('-') + 1:]
                    current_gmt = time.gmtime()
                    time_stamp = calendar.timegm(current_gmt)
                    file.name = f'{time_stamp}-{uuid4().hex}.{file.name.split(".")[-1]}'
                    ArticleFile.objects.create(file=file, article=art, name=name)
                return JsonResponse({'result': 'ok'})
            except:
                pass
    else:
        return JsonResponse({'result': 'captcha'})

    return JsonResponse({'result': 'failed'})


@login_required
def delete_article(request):
    pk = int(request.POST.get('pk'))
    Article.objects.get(pk=pk).delete()
    return JsonResponse({'result': 'ok'})


@login_required
def delete_application(request):
    pk = int(request.POST.get('pk'))
    ArticleApprovalApplication.objects.get(pk=pk).article.delete()
    return JsonResponse({'result': 'ok'})


@login_required
def hide_article(request):
    pk = int(request.POST.get('pk'))
    art = Article.objects.get(pk=pk)
    art.hidden = not art.hidden
    art.save()
    return JsonResponse({'result': 'ok'})

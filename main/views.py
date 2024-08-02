from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import ListView
from custom.models import Page, Section
from .models import QuestionAnswer, Review, MainSliderImage, Application, Place, News, SiteContent, Banner, IndexLink
from django.conf import settings
from django.core.mail import send_mail
from MedProject.settings import BASE_URL
from .serializers import NewsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.dateparse import parse_date




def index(request):
    colors = ['#4F55DA', '#F06445', '#E8C444', '#B8D935', '#4FC9DA']
    questions_set = QuestionAnswer.objects.filter(approved=True).order_by('-id')[0:5:1]
    questions_list = []

    for i, review in enumerate(questions_set):
        questions_list.append((review, colors[i % 5]))

    slides = [{'image': i.image.url,
               'link': i.link if i.link is not None else ''} for i in MainSliderImage.objects.all().order_by('order')]
    banners = [{'image': i.image.url, 'link': i.link, 'name': i.name} for i in Banner.objects.all().order_by('-pk')]
    links = [{'image': i.image.url if bool(i.image) else '', 'link': i.link, 'name': i.name} for i in IndexLink.objects.all().order_by('-pk')]

    links_display = True
    try:
        links_display = int(SiteContent.objects.get(name='index_links_display').content)
    except ValueError:
        pass

    context = {
        'title': 'Главная',
        'menu_sections': Section.objects.all().order_by('order'),
        'account_section_id': int(SiteContent.objects.get(name='account_section_id').content),
        'menu_pages': Page.objects.filter(section=None),
        'header_content': [SiteContent.objects.get(name='email').content,
                                     SiteContent.objects.get(name='phone').content,
                                     SiteContent.objects.get(name='phone').content.translate(
                                         str.maketrans({' ': '', '-': '', '(': '', ')': ''}))],
        'slides': slides,
        'banners': banners,
        'news': News.objects.all().order_by('order', '-pk')[0:6:1],
        # 'questions': questions_list
        'text': SiteContent.objects.get(name='index_text').content,
        'links': links,
        'links_display': links_display,
        'links_label': SiteContent.objects.get(name='index_links_label').content,
    }

    return render(request, 'main/index.html', context)


class ReviewsList(ListView):
    model = Review
    template_name = 'main/reviews.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Отзывы'
        context['menu_sections'] = Section.objects.all().order_by('order')
        context['account_section_id'] = int(SiteContent.objects.get(name='account_section_id').content)
        context['menu_pages'] = Page.objects.filter(section=None)
        context['header_content'] = [SiteContent.objects.get(name='email').content,
                                     SiteContent.objects.get(name='phone').content,
                                     SiteContent.objects.get(name='phone').content.translate(
                                         str.maketrans({' ': '', '-': '', '(': '', ')': ''}))]

        return context

    def get_queryset(self):
        colors = ['#4F55DA', '#F06445', '#E8C444', '#B8D935', '#4FC9DA']
        reviews_set = Review.objects.filter(approved=True).order_by('-pk')
        reviews_list = []

        for i, review in enumerate(reviews_set):
            reviews_list.append((review, colors[i % 5]))
        return reviews_list


def create_review(request):

    name = request.POST.get('name')
    text = request.POST.get('text')

    if request.recaptcha_is_valid:
        if name and text:
            try:
                Review.objects.create(text=text, name=name)
                return JsonResponse({'result': 'ok'})
            except:
                pass
    else:
        return JsonResponse({'result': 'captcha'})

    return JsonResponse({'result': 'failed'})


class FaqView(ListView):
    model = QuestionAnswer
    template_name = 'main/faq.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вопрос - ответ'
        context['menu_sections'] = Section.objects.all().order_by('order')
        context['account_section_id'] = int(SiteContent.objects.get(name='account_section_id').content)
        context['menu_pages'] = Page.objects.filter(section=None)
        context['header_content'] = [SiteContent.objects.get(name='email').content,
                                     SiteContent.objects.get(name='phone').content,
                                     SiteContent.objects.get(name='phone').content.translate(
                                         str.maketrans({' ': '', '-': '', '(': '', ')': ''}))]

        return context

    def get_queryset(self):
        colors = ['#4F55DA', '#F06445', '#E8C444', '#B8D935', '#4FC9DA']
        questions_set = QuestionAnswer.objects.filter(approved=True).order_by('-pk')
        questions_list = []

        for i, question in enumerate(questions_set):
            questions_list.append((question, colors[i % 5]))
        return questions_list


def create_question(request):

    name = request.POST.get('name')
    question = request.POST.get('question')

    if request.recaptcha_is_valid:
        if name and question:
            try:
                QuestionAnswer.objects.create(question=question, name=name)
                return JsonResponse({'result': 'ok'})
            except:
                pass
    else:
        return JsonResponse({'result': 'captcha'})

    return JsonResponse({'result': 'failed'})


def consultation(request):

    context = {
        'title': 'Интерактивная консультация',
        'menu_sections': Section.objects.all().order_by('order'),
        'account_section_id': int(SiteContent.objects.get(name='account_section_id').content),
        'menu_pages': Page.objects.filter(section=None),
        'rules_url': SiteContent.objects.get(name='rules_url').content,
        'header_content': [SiteContent.objects.get(name='email').content,
                                     SiteContent.objects.get(name='phone').content,
                                     SiteContent.objects.get(name='phone').content.translate(
                                         str.maketrans({' ': '', '-': '', '(': '', ')': ''}))],
        'text': SiteContent.objects.get(name='application_text').content
    }

    return render(request, 'main/consultation.html', context)


def create_application(request):

    first_name = request.POST.get('name')
    last_name = request.POST.get('surname')
    patronymic = request.POST.get('patronymic')
    email = request.POST.get('email')
    phone_number = request.POST.get('phone_number')
    text = request.POST.get('question')
    address = request.POST.get('address')

    if request.recaptcha_is_valid:
        if first_name and last_name and patronymic and email and phone_number and text:
            try:
                app = Application.objects.create(text=text, first_name=first_name, last_name=last_name, patronymic=patronymic,
                                                 email=email, phone_number=phone_number, address=address)
                if not BASE_URL == 'http://127.0.0.1:8000':
                    message = f'Email: {email}\nСсылка на заявку: {BASE_URL}/admin/main/application/{app.pk}/'
                    send_mail(
                        'Новая заявка на консультацию',
                        message,
                        settings.EMAIL_HOST_USER,
                        [SiteContent.objects.get(name='notification_email').content],
                        fail_silently=False
                    )

                    message = f'{SiteContent.objects.get(name="email_application_message").content}'
                    send_mail(
                        'Ваша заявка на консультацию успешно отправлена',
                        message,
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False
                    )

                return JsonResponse({'result': 'ok'})
            except:
                pass
    else:
        return JsonResponse({'result': 'captcha'})

    return JsonResponse({'result': 'failed'})


def geography(request):

    context = {
        'title': 'География ранней помощи',
        'menu_sections': Section.objects.all().order_by('order'),
        'account_section_id': int(SiteContent.objects.get(name='account_section_id').content),
        'menu_pages': Page.objects.filter(section=None),
        'header_content': [SiteContent.objects.get(name='email').content,
                                     SiteContent.objects.get(name='phone').content,
                                     SiteContent.objects.get(name='phone').content.translate(
                                         str.maketrans({' ': '', '-': '', '(': '', ')': ''}))],
        'places': Place.objects.all().order_by('order')
    }

    return render(request, 'main/geography.html', context)


class NewsList(ListView):
    model = News
    template_name = 'main/news.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Новости'
        context['menu_sections'] = Section.objects.all().order_by('order')
        context['account_section_id'] = int(SiteContent.objects.get(name='account_section_id').content)
        context['menu_pages'] = Page.objects.filter(section=None)
        context['header_content'] = [SiteContent.objects.get(name='email').content,
                                     SiteContent.objects.get(name='phone').content,
                                     SiteContent.objects.get(name='phone').content.translate(
                                         str.maketrans({' ': '', '-': '', '(': '', ')': ''}))]

        return context

    def get_queryset(self):
        colors = ['#4F55DA', '#F06445', '#E8C444', '#B8D935', '#4FC9DA']
        news_set = News.objects.all().order_by('order','-pk')
        news_list = []

        for i, n in enumerate(news_set):
            news_list.append((n, colors[i % 5]))
        return news_list


def single_news(request, pk):

    current_news = News.objects.get(pk=int(pk))

    context = {
        'title': current_news.title,
        'menu_sections': Section.objects.all().order_by('order'),
        'account_section_id': int(SiteContent.objects.get(name='account_section_id').content),
        'menu_pages': Page.objects.filter(section=None),
        'header_content': [SiteContent.objects.get(name='email').content,
                                     SiteContent.objects.get(name='phone').content,
                                     SiteContent.objects.get(name='phone').content.translate(
                                         str.maketrans({' ': '', '-': '', '(': '', ')': ''}))],
        'current_news': current_news
    }

    return render(request, 'main/single_news.html', context)

# class NewsSearchView(APIView):
#     def get(self, request):
#         query = request.GET.get('query', '')
#         news = News.objects.filter(title__icontains=query) | News.objects.filter(content__icontains=query)
#         serializer = NewsSerializer(news, many=True)
#         return Response(serializer.data)
class NewsSearchView(APIView):
    def get(self, request):
        query = request.GET.get('query', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')

        news = News.objects.all()

        if query:
            news = news.filter(title__icontains=query) | news.filter(content__icontains=query)

        if date_from:
            date_from = parse_date(date_from)
            news = news.filter(date__gte=date_from)

        if date_to:
            date_to = parse_date(date_to)
            news = news.filter(date__lte=date_to)
        
        # Сортировка по дате (новые вверху)
        news = news.order_by('-date')

        serializer = NewsSerializer(news, many=True)
        return Response(serializer.data)
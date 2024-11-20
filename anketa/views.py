from django.shortcuts import render
from custom.models import Page, Section
from main.models import SiteContent
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import messages
from main.models import Place, Institution
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
import matplotlib
matplotlib.use('Agg')  # Устанавливаем бэкенд перед импортом pyplot
import matplotlib.pyplot as plt
import io
import base64
import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Anketa


from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse



@method_decorator(login_required, name='dispatch')
class BaseStatisticsView(TemplateView):
    template_name = "admin/statistics.html"
    group_by_field = None
    title = "Статистика"

    def get(self, request, *args, **kwargs):
        # Проверяем наличие параметра `export=excel` в GET-запросе
        if request.GET.get('export') == 'excel':
            start_date = request.GET.get('start_date', (timezone.now() - timezone.timedelta(days=7)).strftime('%Y-%m-%d'))
            end_date = request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))
            queryset = Anketa.objects.filter(created_at__range=[start_date, end_date])
            statistics = queryset.values(f'{self.group_by_field}__name').annotate(count=Count('id')).order_by('-count')
            return self.export_to_excel(statistics, start_date, end_date)

        # Если экспорт не запрашивается, вызываем стандартный метод `get()`
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        start_date = self.request.GET.get('start_date', (timezone.now() - timezone.timedelta(days=7)).strftime('%Y-%m-%d'))
        end_date = self.request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))
        show_top_10 = self.request.GET.get('show_top_10') == 'on'

        queryset = Anketa.objects.filter(created_at__range=[start_date, end_date])
        statistics = queryset.values(f'{self.group_by_field}__name').annotate(count=Count('id')).order_by('-count')

        total_count = queryset.count()
        others_count = 0

        chart_base64 = None
        if show_top_10 and len(statistics) > 10:
            top_10 = list(statistics[:10])
            others_count = sum(item['count'] for item in statistics[10:])
            max_count = max(item['count'] for item in top_10)

            if others_count <= 2 * max_count:
                top_10.append({f'{self.group_by_field}__name': 'Прочие', 'count': others_count})

            statistics = top_10

            labels = [item[f'{self.group_by_field}__name'] for item in statistics]
            counts = [item['count'] for item in statistics]

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors, textprops={'fontsize': 8})
            ax.set_title(f'Распределение заявок по {self.title} (Топ-10)', fontsize=10)

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            plt.close(fig)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            chart_base64 = f"data:image/png;base64,{image_base64}"

        context.update({
            'statistics': statistics,
            'total_count': total_count,
            'others_count': others_count,
            'start_date': start_date,
            'end_date': end_date,
            'show_top_10': show_top_10,
            'chart_base64': chart_base64,
            'title': self.title,
        })
        return context

    def export_to_excel(self, statistics, start_date, end_date):
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Статистика"

        headers = [self.title, "Количество заявок"]
        for col_num, header in enumerate(headers, 1):
            col_letter = get_column_letter(col_num)
            worksheet[f"{col_letter}1"] = header

        for row_num, item in enumerate(statistics, 2):
            worksheet[f"A{row_num}"] = item[f'{self.group_by_field}__name']
            worksheet[f"B{row_num}"] = item['count']

        worksheet[f"A{row_num + 1}"] = "Всего"
        worksheet[f"B{row_num + 1}"] = sum(item['count'] for item in statistics)

        worksheet.column_dimensions["A"].width = 30
        worksheet.column_dimensions["B"].width = 20

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="statistics_{start_date}_{end_date}.xlsx"'
        workbook.save(response)
        return response




class StatisticsByInstitutionView(BaseStatisticsView):
    group_by_field = 'institution'
    title = "Учреждение"

class StatisticsByCityView(BaseStatisticsView):
    group_by_field = 'city'
    title = "Город"




def get_relation_statistics(queryset):
    """
    Возвращает статистику по степеням родства.
    """
    relation_choices = dict(Anketa.RELATION_CHOICES)
    statistics = queryset.values('relation').annotate(count=Count('id')).order_by('-count')

    # Преобразуем ключи в их человекочитаемые значения
    formatted_statistics = [
        {'relation': relation_choices[item['relation']], 'count': item['count']}
        for item in statistics
    ]

    return formatted_statistics

class StatisticsByRelationView(TemplateView):
    template_name = "admin/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        start_date = self.request.GET.get('start_date', (timezone.now() - timezone.timedelta(days=7)).strftime('%Y-%m-%d'))
        end_date = self.request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))

        queryset = Anketa.objects.filter(created_at__range=[start_date, end_date])
        statistics = queryset.values('relation').annotate(count=Count('id')).order_by('-count')

        # Преобразуем ключи в человекочитаемые значения
        relation_choices = dict(Anketa.RELATION_CHOICES)
        formatted_statistics = [
            {'relation': relation_choices.get(item['relation'], "Не указано"), 'count': item['count']}
            for item in statistics
        ]

        total_count = sum(item['count'] for item in statistics)

        context.update({
            'statistics': formatted_statistics,
            'total_count': total_count,
            'title': "Статистика по степеням родства",
            'start_date': start_date,
            'end_date': end_date,
        })
        return context
    def get(self, request, *args, **kwargs):
        if request.GET.get('export') == 'excel':
            start_date = request.GET.get('start_date', (timezone.now() - timezone.timedelta(days=7)).strftime('%Y-%m-%d'))
            end_date = request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))

            queryset = Anketa.objects.filter(created_at__range=[start_date, end_date])
            statistics = get_relation_statistics(queryset)

            # Экспортируем данные
            return self.export_to_excel(statistics, start_date, end_date)

        return super().get(request, *args, **kwargs)
    def export_to_excel(self, statistics, start_date, end_date):
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Статистика по степеням родства"

        headers = ["Степень родства", "Количество заявок"]
        for col_num, header in enumerate(headers, 1):
            col_letter = get_column_letter(col_num)
            worksheet[f"{col_letter}1"] = header

        for row_num, item in enumerate(statistics, 2):
            worksheet[f"A{row_num}"] = item['relation']
            worksheet[f"B{row_num}"] = item['count']

        worksheet[f"A{row_num + 1}"] = "Всего"
        worksheet[f"B{row_num + 1}"] = sum(item['count'] for item in statistics)

        worksheet.column_dimensions["A"].width = 30
        worksheet.column_dimensions["B"].width = 20

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="relation_statistics_{start_date}_{end_date}.xlsx"'
        workbook.save(response)
        return response








@csrf_exempt
def anketa_view(request):
    if request.method == 'POST':
        # Определяем, является ли запрос AJAX
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        # Получаем данные из POST-запроса
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        relation = request.POST.get('relation')
        relation_other = request.POST.get('relation_other')
        main_phone = request.POST.get('main_phone')
        additional_phone = request.POST.get('additional_phone')
        main_email = request.POST.get('main_email')
        additional_email = request.POST.get('additional_email')
        preferred_contact = request.POST.getlist('preferred_contact')
        preferred_time = request.POST.get('preferred_time')
        child_last_name = request.POST.get('child_last_name')
        child_first_name = request.POST.get('child_first_name')
        child_middle_name = request.POST.get('child_middle_name')
        child_birth_date = request.POST.get('child_birth_date')
        city_id = request.POST.get('city')
        city = Place.objects.get(id=city_id) if city_id else None
        street = request.POST.get('street')
        house = request.POST.get('house')
        apartment = request.POST.get('apartment')
        reasons = request.POST.getlist('reasons')
        reason_other = request.POST.get('reason_other')
        referral_document = request.FILES.get('referral_document')
        sources = request.POST.getlist('sources')
        source_other = request.POST.get('source_other')
        consent = request.POST.get('consent') == 'on'

        # Серверная валидация данных
        errors = []

        # Пример простой валидации
        if not last_name:
            errors.append('Фамилия обязательна.')
        if not first_name:
            errors.append('Имя обязательно.')
        if not main_phone:
            errors.append('Основной номер телефона обязателен.')
        if not main_email:
            errors.append('Основной электронный адрес обязателен.')
        if not child_last_name:
            errors.append('Фамилия ребенка обязательна.')
        if not child_first_name:
            errors.append('Имя ребенка обязательно.')
        if not child_birth_date:
            errors.append('Дата рождения ребенка обязательна.')
        if not street:
            errors.append('Улица/микрорайон обязательны.')
        if not house:
            errors.append('Дом обязателен.')

        # Проверка обязательных полей и других условий
        # Добавьте дополнительные проверки по необходимости

        if is_ajax:
            if errors:
                return JsonResponse({'success': False, 'errors': errors})
            try:
                # Сохранение данных в модель Anketa
                anketa = Anketa(
                    last_name=last_name,
                    first_name=first_name,
                    middle_name=middle_name,
                    relation=relation,
                    relation_other=relation_other,
                    main_phone=main_phone,
                    additional_phone=additional_phone,
                    main_email=main_email,
                    additional_email=additional_email,
                    preferred_contact=preferred_contact,
                    preferred_time=preferred_time,
                    child_last_name=child_last_name,
                    child_first_name=child_first_name,
                    child_middle_name=child_middle_name,
                    child_birth_date=child_birth_date,
                    city=city,
                    street=street,
                    house=house,
                    apartment=apartment,
                    reasons=reasons,
                    reason_other=reason_other,
                    referral_document=referral_document,
                    sources=sources,
                    source_other=source_other,
                    consent=consent
                )
                anketa.save()
                return JsonResponse({'success': True})
            except Exception as e:
                # Логирование ошибки может быть добавлено здесь
                return JsonResponse({'success': False, 'errors': ['Произошла ошибка при сохранении анкеты.']})
        else:
            # Обработка обычного POST-запроса без AJAX
            if errors:
                # Здесь вы можете добавить сообщения об ошибках, например, используя Django messages
                return redirect('anketa')  # Или другой подход по обработке ошибок
            try:
                anketa = Anketa(
                    last_name=last_name,
                    first_name=first_name,
                    middle_name=middle_name,
                    relation=relation,
                    relation_other=relation_other,
                    main_phone=main_phone,
                    additional_phone=additional_phone,
                    main_email=main_email,
                    additional_email=additional_email,
                    preferred_contact=preferred_contact,
                    preferred_time=preferred_time,
                    child_last_name=child_last_name,
                    child_first_name=child_first_name,
                    child_middle_name=child_middle_name,
                    child_birth_date=child_birth_date,
                    city=city,
                    street=street,
                    house=house,
                    apartment=apartment,
                    reasons=reasons,
                    reason_other=reason_other,
                    referral_document=referral_document,
                    sources=sources,
                    source_other=source_other,
                    consent=consent
                )
                anketa.save()
                return redirect('anketa')
            except Exception as e:
                # Логирование ошибки может быть добавлено здесь
                return redirect('anketa')  # Или другой подход по обработке ошибок

    # Обработка GET-запроса
    cities = Place.objects.all().order_by('name')

    context = {
        'title': 'Анкета на помощь',
        'menu_sections': Section.objects.all().order_by('order'),
        'account_section_id': int(SiteContent.objects.get(name='account_section_id').content),
        'menu_pages': Page.objects.filter(section=None),
        'rules_url': SiteContent.objects.get(name='rules_url').content,
        'header_content': [
            SiteContent.objects.get(name='email').content,
            SiteContent.objects.get(name='phone').content,
            SiteContent.objects.get(name='phone').content.translate(str.maketrans({' ': '', '-': '', '(': '', ')': ''}))
        ],
        'cities': cities,  # Передаём список городов в шаблон
    }

    return render(request, 'anketa/anketa.html', context)


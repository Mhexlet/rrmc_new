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
        relation_choices_dict = dict(Anketa.RELATION_CHOICES)
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Статистика"

        headers = [self.title, "Количество заявок"]
        for col_num, header in enumerate(headers, 1):
            col_letter = get_column_letter(col_num)
            worksheet[f"{col_letter}1"] = header

        for row_num, item in enumerate(statistics, 2):
            if self.group_by_field == 'relation':
                display_value = relation_choices_dict.get(item['relation'], item['relation'])
            else:
                display_value = item[f'{self.group_by_field}__name']
            worksheet[f"A{row_num}"] = display_value
            worksheet[f"B{row_num}"] = item['count']

        worksheet[f"A{row_num + 1}"] = "Всего"
        worksheet[f"B{row_num + 1}"] = sum(item['count'] for item in statistics)

        worksheet.column_dimensions["A"].width = 30
        worksheet.column_dimensions["B"].width = 20

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="statistics_{start_date}_{end_date}.xlsx"'
        workbook.save(response)
        return response



class StatisticsByCityView(BaseStatisticsView):
    group_by_field = 'city'
    title = "Город"
class StatisticsByInstitutionView(BaseStatisticsView):
    group_by_field = 'institution'
    title = "Учреждение"
class StatisticsByRelationView(BaseStatisticsView):
    group_by_field = 'relation'
    title = "Степень родства"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Создаём словарь для замены значений на человекочитаемые
        relation_choices_dict = dict(Anketa.RELATION_CHOICES)
        statistics = context['statistics']

        # Заменяем значения relation на человекочитаемые из словаря
        for item in statistics:
            relation_code = item['relation']
            item['relation_display'] = relation_choices_dict.get(relation_code, relation_code)

        context['statistics'] = statistics
        return context



# class StatisticsView(TemplateView):
#     template_name = "admin/statistics.html"

#     def get(self, request, *args, **kwargs):
#         # Если запрос на экспорт в Excel, сразу вызываем метод экспорта
#         if request.GET.get('export') == 'excel':
#             start_date = request.GET.get('start_date', (timezone.now() - timezone.timedelta(days=7)).strftime('%Y-%m-%d'))
#             end_date = request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))
#             queryset = Anketa.objects.filter(date_processed__range=[start_date, end_date])
#             statistics = queryset.values('institution__name').annotate(count=Count('id')).order_by('-count')
#             return self.export_to_excel(statistics, start_date, end_date)

#         # В остальных случаях возвращаем стандартное представление
#         return super().get(request, *args, **kwargs)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         start_date = self.request.GET.get('start_date', (timezone.now() - timezone.timedelta(days=7)).strftime('%Y-%m-%d'))
#         end_date = self.request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))
#         show_top_10 = self.request.GET.get('show_top_10') == 'on'

#         queryset = Anketa.objects.filter(date_processed__range=[start_date, end_date])
#         statistics = queryset.values('institution__name').annotate(count=Count('id')).order_by('-count')

#         total_count = queryset.count()
#         institutions_count = statistics.count()
#         others_count = 0

#         chart_base64 = None
#         if show_top_10 and institutions_count > 10:
#             top_10 = list(statistics[:10])
#             others_count = sum(item['count'] for item in statistics[10:])
#             max_count = max(item['count'] for item in top_10)

#             if others_count <= 2 * max_count:
#                 top_10.append({'institution__name': 'Прочие', 'count': others_count})

#             statistics = top_10

#             labels = [item['institution__name'] for item in statistics]
#             counts = [item['count'] for item in statistics]

#             fig, ax = plt.subplots(figsize=(6, 4))
#             ax.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors, textprops={'fontsize': 8})
#             ax.set_title('Распределение заявок по учреждениям (Топ-10)', fontsize=10)

#             buffer = io.BytesIO()
#             plt.savefig(buffer, format='png', bbox_inches='tight')
#             plt.close(fig)
#             buffer.seek(0)
#             image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
#             chart_base64 = f"data:image/png;base64,{image_base64}"

#         context.update({
#             'statistics': statistics,
#             'total_count': total_count,
#             'institutions_count': institutions_count,
#             'others_count': others_count,
#             'start_date': start_date,
#             'end_date': end_date,
#             'show_top_10': show_top_10,
#             'chart_base64': chart_base64,
#         })
#         return context

#     def export_to_excel(self, statistics, start_date, end_date):
#         import openpyxl
#         from openpyxl.utils import get_column_letter
#         from django.http import HttpResponse

#         # Проверяем, требуется ли экспорт только топ-10
#         show_top_10 = self.request.GET.get('show_top_10') == 'on'
#         if show_top_10 and len(statistics) > 10:
#             top_10 = list(statistics[:10])
#             others_count = sum(item['count'] for item in statistics[10:])
#             max_count = max(item['count'] for item in top_10)

#             # Проверяем условие отображения "Прочие"
#             if others_count <= 2 * max_count:
#                 top_10.append({'institution__name': 'Прочие', 'count': others_count})

#             statistics = top_10

#         # Создаём новый Excel файл
#         workbook = openpyxl.Workbook()
#         worksheet = workbook.active
#         worksheet.title = "Статистика по учреждениям"

#         # Заполняем заголовки
#         headers = ["Учреждение", "Количество заявок"]
#         for col_num, header in enumerate(headers, 1):
#             col_letter = get_column_letter(col_num)
#             worksheet[f"{col_letter}1"] = header

#         # Заполняем данные
#         for row_num, item in enumerate(statistics, 2):
#             worksheet[f"A{row_num}"] = item['institution__name']
#             worksheet[f"B{row_num}"] = item['count']

#         # Добавляем итоговую строку
#         worksheet[f"A{row_num + 1}"] = "Всего"
#         worksheet[f"B{row_num + 1}"] = sum(item['count'] for item in statistics)

#         # Настраиваем ширину столбцов
#         worksheet.column_dimensions["A"].width = 30
#         worksheet.column_dimensions["B"].width = 20

#         # Возвращаем файл как ответ
#         response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
#         response["Content-Disposition"] = f'attachment; filename="statistics_{start_date}_{end_date}.xlsx"'
#         workbook.save(response)
#         return response




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





# def anketa_view(request):
#     if request.method == 'POST':
#         # Определяем, является ли запрос AJAX
#         is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

#         # Получаем данные из POST-запроса
#         last_name = request.POST.get('last_name')
#         first_name = request.POST.get('first_name')
#         middle_name = request.POST.get('middle_name')
#         relation = request.POST.get('relation')
#         relation_other = request.POST.get('relation_other')
#         main_phone = request.POST.get('main_phone')
#         additional_phone = request.POST.get('additional_phone')
#         main_email = request.POST.get('main_email')
#         additional_email = request.POST.get('additional_email')
#         preferred_contact = request.POST.getlist('preferred_contact')
#         preferred_time = request.POST.get('preferred_time')
#         child_last_name = request.POST.get('child_last_name')
#         child_first_name = request.POST.get('child_first_name')
#         child_middle_name = request.POST.get('child_middle_name')
#         child_birth_date = request.POST.get('child_birth_date')
#         city_id = request.POST.get('city')
#         city = Place.objects.get(id=city_id) if city_id else None
#         street = request.POST.get('street')
#         house = request.POST.get('house')
#         apartment = request.POST.get('apartment')
#         reasons = request.POST.getlist('reasons')
#         reason_other = request.POST.get('reason_other')
#         referral_document = request.FILES.get('referral_document')
#         sources = request.POST.getlist('sources')
#         source_other = request.POST.get('source_other')
#         consent = request.POST.get('consent') == 'on'

#         # Здесь вы можете добавить серверную валидацию данных
#         errors = []

#         # Пример простой валидации
#         if not last_name:
#             errors.append('Фамилия обязательна.')
#         if not first_name:
#             errors.append('Имя обязательно.')
#         # Добавьте другие проверки по необходимости

#         if is_ajax:
#             if errors:
#                 return JsonResponse({'success': False, 'errors': errors})
#             try:
#                 # Сохранение данных в модель Anketa
#                 anketa = Anketa(
#                     last_name=last_name,
#                     first_name=first_name,
#                     middle_name=middle_name,
#                     relation=relation,
#                     relation_other=relation_other,
#                     main_phone=main_phone,
#                     additional_phone=additional_phone,
#                     main_email=main_email,
#                     additional_email=additional_email,
#                     preferred_contact=preferred_contact,
#                     preferred_time=preferred_time,
#                     child_last_name=child_last_name,
#                     child_first_name=child_first_name,
#                     child_middle_name=child_middle_name,
#                     child_birth_date=child_birth_date,
#                     city=city,
#                     street=street,
#                     house=house,
#                     apartment=apartment,
#                     reasons=reasons,
#                     reason_other=reason_other,
#                     referral_document=referral_document,
#                     sources=sources,
#                     source_other=source_other,
#                     consent=consent
#                 )
#                 anketa.save()
#                 return JsonResponse({'success': True})
#             except Exception as e:
#                 # Логирование ошибки может быть добавлено здесь
#                 return JsonResponse({'success': False, 'errors': ['Произошла ошибка при сохранении анкеты.']})
#         else:
#             # Обработка обычного POST-запроса без AJAX
#             if errors:
#                 # Здесь вы можете добавить сообщения об ошибках, например, используя Django messages
#                 return redirect('anketa')  # Или другой подход по обработке ошибок
#             try:
#                 anketa = Anketa(
#                     last_name=last_name,
#                     first_name=first_name,
#                     middle_name=middle_name,
#                     relation=relation,
#                     relation_other=relation_other,
#                     main_phone=main_phone,
#                     additional_phone=additional_phone,
#                     main_email=main_email,
#                     additional_email=additional_email,
#                     preferred_contact=preferred_contact,
#                     preferred_time=preferred_time,
#                     child_last_name=child_last_name,
#                     child_first_name=child_first_name,
#                     child_middle_name=child_middle_name,
#                     child_birth_date=child_birth_date,
#                     city=city,
#                     street=street,
#                     house=house,
#                     apartment=apartment,
#                     reasons=reasons,
#                     reason_other=reason_other,
#                     referral_document=referral_document,
#                     sources=sources,
#                     source_other=source_other,
#                     consent=consent
#                 )
#                 anketa.save()
#                 return redirect('anketa')
#             except Exception as e:
#                 # Логирование ошибки может быть добавлено здесь
#                 return redirect('anketa')  # Или другой подход по обработке ошибок

#     # Обработка GET-запроса
#     cities = Place.objects.all().order_by('name')

#     context = {
#         'title': 'Анкета на помощь',
#         'menu_sections': Section.objects.all().order_by('order'),
#         'account_section_id': int(SiteContent.objects.get(name='account_section_id').content),
#         'menu_pages': Page.objects.filter(section=None),
#         'rules_url': SiteContent.objects.get(name='rules_url').content,
#         'header_content': [
#             SiteContent.objects.get(name='email').content,
#             SiteContent.objects.get(name='phone').content,
#             SiteContent.objects.get(name='phone').content.translate(str.maketrans({' ': '', '-': '', '(': '', ')': ''}))
#         ],
#         'cities': cities,  # Передаём список городов в шаблон
#     }

#     return render(request, 'anketa/anketa.html', context)
# def anketa_view(request):
#     if request.method == 'POST':
#         # Получаем данные из POST-запроса
#         last_name = request.POST.get('last_name')
#         first_name = request.POST.get('first_name')
#         middle_name = request.POST.get('middle_name')
#         relation = request.POST.get('relation')
#         relation_other = request.POST.get('relation_other')
#         main_phone = request.POST.get('main_phone')
#         additional_phone = request.POST.get('additional_phone')
#         main_email = request.POST.get('main_email')
#         additional_email = request.POST.get('additional_email')
#         preferred_contact = request.POST.getlist('preferred_contact')
#         preferred_time = request.POST.get('preferred_time')
#         child_last_name = request.POST.get('child_last_name')
#         child_first_name = request.POST.get('child_first_name')
#         child_middle_name = request.POST.get('child_middle_name')
#         child_birth_date = request.POST.get('child_birth_date')
#         # city = request.POST.get('city')
#         # Получаем объект города из модели Place
#         city_id = request.POST.get('city')
#         city = Place.objects.get(id=city_id) if city_id else None

#         street = request.POST.get('street')
#         house = request.POST.get('house')
#         apartment = request.POST.get('apartment')
#         reasons = request.POST.getlist('reasons')
#         reason_other = request.POST.get('reason_other')
#         referral_document = request.FILES.get('referral_document')
#         sources = request.POST.getlist('sources')
#         source_other = request.POST.get('source_other')
#         consent = request.POST.get('consent') == 'on'

#         # Сохранение данных в модель Anketa
#         anketa = Anketa(
#             last_name=last_name,
#             first_name=first_name,
#             middle_name=middle_name,
#             relation=relation,
#             relation_other=relation_other,
#             main_phone=main_phone,
#             additional_phone=additional_phone,
#             main_email=main_email,
#             additional_email=additional_email,
#             preferred_contact=preferred_contact,
#             preferred_time=preferred_time,
#             child_last_name=child_last_name,
#             child_first_name=child_first_name,
#             child_middle_name=child_middle_name,
#             child_birth_date=child_birth_date,
#             city=city,
#             street=street,
#             house=house,
#             apartment=apartment,
#             reasons=reasons,
#             reason_other=reason_other,
#             referral_document=referral_document,
#             sources=sources,
#             source_other=source_other,
#             consent=consent
#         )

#         # Сохраняем запись в базе данных
#         anketa.save()
#         # messages.success(request, 'Анкета успешно отправлена!')
#         return redirect('anketa')
    
#     # Получаем список городов из модели Place
#     cities = Place.objects.all().order_by('name')

#     context = {
#         'title': 'Анкета на помощь',
#         'menu_sections': Section.objects.all().order_by('order'),
#         'account_section_id': int(SiteContent.objects.get(name='account_section_id').content),
#         'menu_pages': Page.objects.filter(section=None),
#         'rules_url': SiteContent.objects.get(name='rules_url').content,
#         'header_content': [
#             SiteContent.objects.get(name='email').content,
#             SiteContent.objects.get(name='phone').content,
#             SiteContent.objects.get(name='phone').content.translate(str.maketrans({' ': '', '-': '', '(': '', ')': ''}))
#         ],
#         'cities': cities,  # Передаём список городов в шаблон
#     }

#     return render(request, 'anketa/anketa.html', context)

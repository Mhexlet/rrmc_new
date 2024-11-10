from django.shortcuts import render
from custom.models import Page, Section
from main.models import SiteContent
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import messages
from main.models import Place, Institution
from django.contrib.admin.views.decorators import staff_member_required


from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse



from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Anketa
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

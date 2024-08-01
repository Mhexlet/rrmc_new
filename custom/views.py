import time
from uuid import uuid4
import calendar
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from custom.models import Section, Page, AlbumBlock, FileSetBlock, AlbumImage, FileSetFile
from main.models import SiteContent


def constructor(request, url):

    page = Page.objects.get(url=url)

    context = {
        'title': page.title,
        'albums': AlbumBlock.objects.filter(page__url=url),
        'filesets': FileSetBlock.objects.filter(page__url=url),
        'current_page': page,
        'menu_sections': Section.objects.all().order_by('order'),
        'account_section_id': int(SiteContent.objects.get(name='account_section_id').content),
        'menu_pages': Page.objects.filter(section=None),
        'header_content': [SiteContent.objects.get(name='email').content,
                                     SiteContent.objects.get(name='phone').content,
                                     SiteContent.objects.get(name='phone').content.translate(
                                         str.maketrans({' ': '', '-': '', '(': '', ')': ''}))]
    }
    return render(request, 'custom/page.html', context)


@user_passes_test(lambda u: u.is_superuser)
def add_album_page(request):

    context = {
        'title': 'Добавление альбома',
        'pages': Page.objects.all()
    }
    return render(request, 'custom/add_album_page.html', context)


@user_passes_test(lambda u: u.is_superuser)
def add_album(request):

    name = request.POST.get('name')
    page_pk = request.POST.get('page')

    if name and page_pk:
        try:
            album = AlbumBlock.objects.create(name=name, page=Page.objects.get(pk=int(page_pk)))
            for pk_name, image in request.FILES.items():
                name = pk_name[pk_name.index('-') + 1:]
                AlbumImage.objects.create(image=image, album=album, name=name)
            return JsonResponse({'result': 'ok'})
        except:
            pass

    return JsonResponse({'result': 'failed'})


@user_passes_test(lambda u: u.is_superuser)
def add_fileset_page(request):

    context = {
        'title': 'Добавление набора файлов',
        'pages': Page.objects.all()
    }
    return render(request, 'custom/add_fileset_page.html', context)


@user_passes_test(lambda u: u.is_superuser)
def add_fileset(request):

    name = request.POST.get('name')
    page_pk = request.POST.get('page')

    if name and page_pk:
        try:
            file_set = FileSetBlock.objects.create(name=name, page=Page.objects.get(pk=int(page_pk)))
            for pk_name, file in request.FILES.items():
                current_gmt = time.gmtime()
                time_stamp = calendar.timegm(current_gmt)
                file.name = f'{time_stamp}-{uuid4().hex}.{file.name.split(".")[-1]}'
                name = pk_name[pk_name.index('-') + 1:]
                FileSetFile.objects.create(file=file, file_set=file_set, name=name)
            return JsonResponse({'result': 'ok'})
        except:
            pass

    return JsonResponse({'result': 'failed'})
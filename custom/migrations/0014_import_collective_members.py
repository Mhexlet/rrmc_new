import html as html_mod
import re

from django.db import migrations


def parse_members(content):
    """Достаёт (фото, ФИО, должность) из HTML-таблицы старой страницы «Коллектив»."""
    members = []
    for cell in re.findall(r'<td[^>]*>(.*?)</td>', content, re.S):
        photo_match = re.search(r'<img[^>]+src="([^"]+)"', cell)
        if not photo_match:
            continue
        photo = photo_match.group(1)
        if photo.startswith('/media/'):
            photo = photo[len('/media/'):]
        text = re.sub(r'<img[^>]*>', '', cell)
        lines = []
        for para in re.findall(r'<p[^>]*>(.*?)</p>', text, re.S):
            line = re.sub(r'<[^>]+>', '', para)
            line = html_mod.unescape(line).replace('\xa0', ' ').strip()
            if line:
                lines.append(line)
        if not lines:
            continue
        members.append({
            'photo': photo,
            'full_name': lines[0],
            'profession': lines[1] if len(lines) > 1 else '',
        })
    return members


def import_members(apps, schema_editor):
    Page = apps.get_model('custom', 'Page')
    CollectiveMember = apps.get_model('custom', 'CollectiveMember')

    if CollectiveMember.objects.exists():
        return

    page = Page.objects.filter(url='collective').first()
    if page is None:
        return

    for order, member in enumerate(parse_members(page.content), start=1):
        CollectiveMember.objects.create(
            full_name=member['full_name'][:128],
            profession=member['profession'][:128],
            photo=member['photo'],
            order=order * 10,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0013_collectivemember'),
    ]

    operations = [
        migrations.RunPython(import_members, migrations.RunPython.noop),
    ]

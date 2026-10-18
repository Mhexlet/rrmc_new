from django.test import SimpleTestCase

from main.editor_content import clean_editor_html


class CleanEditorHtmlTests(SimpleTestCase):

    def test_removes_css_pasted_as_paragraph(self):
        # Так CKEditor 5 сохраняет вставленный <style>: CSS становится текстом абзаца
        html = (
            '<p><a href="https://reestr.eii.ru/">Подать заявку</a></p>'
            '<p>.btn { display: block; /* Строчно-блочный элемент */ margin: 0 auto; '
            'background: #13CAD7; border-radius: 5px; /* Скругляем уголки */ }&nbsp;</p>'
            '<p>Дальше обычный текст.</p>'
        )
        cleaned, removed = clean_editor_html(html)
        self.assertTrue(removed)
        self.assertEqual(
            cleaned,
            '<p><a href="https://reestr.eii.ru/">Подать заявку</a></p><p>Дальше обычный текст.</p>',
        )

    def test_removes_style_meta_and_title(self):
        html = '<p>Текст</p><meta charset="utf-8"><title>Кнопка</title><style>.btn { color: #fff; }</style>'
        self.assertEqual(clean_editor_html(html), ('<p>Текст</p>', True))

    def test_keeps_broken_img_with_meta_like_attribute(self):
        # Битый тег из старого контента: «<meta» тут атрибут img, а не отдельный тег
        html = '<p><img src="/media/a.jpg" style="width: 100%;" <meta="" charset="utf-8"></p>'
        self.assertEqual(clean_editor_html(html), (html, False))

    def test_keeps_ordinary_text_with_braces_and_colons(self):
        html = (
            '<p>Время работы: пн–пт {кроме праздников}; сб: 10:00–14:00;</p>'
            '<p>Формула {a: b;} в тексте</p>'
            '<p><a class="rr-btn rr-btn--red" href="https://example.com">Записаться</a></p>'
        )
        self.assertEqual(clean_editor_html(html), (html, False))

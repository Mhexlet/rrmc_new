"""Проверка документа направления, который родители прикладывают к анкете.

Форма открыта всем, поэтому боты загружают через неё что угодно, в том числе
PHP-скрипты. Пропускаем только форматы из подсказки на странице и проверяем,
что содержимое файла совпадает с расширением.
"""
import os
import uuid
import zipfile

MAX_REFERRAL_SIZE = 10 * 1024 * 1024  # 10 МБ, как написано в форме

# расширение -> с чего должен начинаться файл
REFERRAL_SIGNATURES = {
    '.pdf': b'%PDF-',
    '.jpg': b'\xff\xd8\xff',
    '.jpeg': b'\xff\xd8\xff',
    '.png': b'\x89PNG\r\n\x1a\n',
    '.docx': b'PK\x03\x04',
}


def check_referral_document(uploaded):
    """Возвращает текст ошибки или None.

    Если файл подходит, даёт ему случайное имя: исходные имена вроде
    «направление.pdf» легко угадать, а файлы лежат в открытой папке media.
    """
    ext = os.path.splitext(uploaded.name)[1].lower()
    signature = REFERRAL_SIGNATURES.get(ext)
    if signature is None:
        return 'Документ направления: допустимы только PDF, JPG, PNG и DOCX.'
    if uploaded.size > MAX_REFERRAL_SIZE:
        return 'Документ направления: размер файла больше 10 МБ.'

    uploaded.seek(0)
    head = uploaded.read(len(signature))
    uploaded.seek(0)
    if head != signature:
        return 'Документ направления: файл повреждён или не соответствует своему формату.'

    if ext == '.docx':
        try:
            with zipfile.ZipFile(uploaded) as archive:
                is_word = 'word/document.xml' in archive.namelist()
        except zipfile.BadZipFile:
            is_word = False
        uploaded.seek(0)
        if not is_word:
            return 'Документ направления: файл повреждён или не соответствует своему формату.'

    uploaded.name = f'{uuid.uuid4().hex}{ext}'
    return None

from django.core.exceptions import ValidationError


def validate_file_size(value):
    max_size = 5 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError("Размер файла не должен превышать 5 МБ.")

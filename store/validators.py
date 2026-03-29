from django.core.exceptions import ValidationError


def validate_file_size(file):
    max_size_kb = 50

    if file.size > max_size_kb * 1024:
        raise ValidationError("Files can not be larger than 50 KB!")

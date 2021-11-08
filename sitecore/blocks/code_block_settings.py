from django.conf import settings


def get_language_choices():
    """
    Default list of language choices, if not overridden by Django.
    """
    DEFAULT_LANGUAGES = (
        ('bash', 'Bash/Shell'),
        ('c', 'C'),
        ('csharp', 'C#'),
        ('cpp', 'C++'),
        ('css', 'CSS'),
        ('diff', 'diff'),
        ('git', 'Git'),
        ('html', 'HTML'),
        ('java', 'Java'),
        ('javascript', 'Javascript'),
        ('json', 'JSON'),
        ('latex', 'LaTeX'),
        ('makefile', 'Makefile'),
        ('markdown', 'Markdown'),
        ('matlab', 'MATLAB'),
        ('powershell', 'PowerShell'),
        ('python', 'Python'),
        ('r', 'R'),
        ('regex', 'Regex'),
        ('ruby', 'Ruby'),
        ('rust', 'Rust'),
        ('scss', 'SCSS'),
        ('yaml', 'YAML'),
    )

    return getattr(settings, "WAGTAIL_CODE_BLOCK_LANGUAGES", DEFAULT_LANGUAGES)


def get_theme():
    """
    Returns a default theme, if not in the proejct's settings. Default theme is 'coy'.
    """

    return getattr(settings, "WAGTAIL_CODE_BLOCK_THEME", "coy")

def get_prism_version():
    prism_version = "1.17.1"

    return prism_version
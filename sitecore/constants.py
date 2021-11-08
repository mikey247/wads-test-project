from pygments.styles import get_all_styles

"""
Sitecore constants module to define several Bootstrap 4, Django and Wagtail constants
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

# Theme and code syntax colour choices

BOOTSTRAP4_THEME_CHOICES = [
    ('default', 'Default Bootstrap 4'),
] + [
    (bsw_theme,'Bootswatch: '+bsw_theme) for bsw_theme in
    ["cerulean", "cosmo", "cyborg", "darkly", "flatly", "journal", "litera", "lumen",
     "lux", "materia", "minty", "pulse", "sandstone", "simplex", "sketchy", "slate",
     "solar", "spacelab", "superhero", "uomhum", "united", "yeti",]
]

PYGMENTS_THEME_CHOICES = [
    (pygment_style,pygment_style) for pygment_style in list(get_all_styles())
]

INITIAL_BOOTSTRAP4_THEME = 'pulse'
INITIAL_PYGMENTS_THEME = 'monokai'

# Navbar settings

NAVBAR_RESPONSIVE_SIZE_CHOICES = [
    ('sm','Small'),
    ('md','Medium'),
    ('lg','Large'),
    ('xl','Extra Large'),
]

NAVBAR_TEXT_COLOUR_MODE = [
    ("navbar-light", "Light"),
    ("navbar-dark", "Dark"),
]

NAVBAR_OUTER_CLASS_DEFAULT = 'container'
NAVBAR_OUTER_CLASS = [
    ('None', 'None'),
    (NAVBAR_OUTER_CLASS_DEFAULT, 'container'),
    ('container-fluid', 'container-fluid'),
]

# Text and colour choices

BOOTSTRAP4_TEXT_ALIGN_CHOICES = (
    ('text-justify', 'Justify'),
    ('text-left', 'Left'),
    ('text-center', 'Centre'),
    ('text-right', 'Right'),
)

BOOTSTRAP4_BACKGROUND_COLOUR_CHOICES = (
    ('bg-primary', 'Primary'),
    ('bg-secondary', 'Secondary'),
    ('bg-transparent', 'Transparent'),
    ('bg-light', 'Light'),
    ('bg-dark', 'Dark'),
    ('bg-white', 'White'),
    ('bg-success', 'Success'),
    ('bg-danger', 'Danger'),
    ('bg-warning', 'Warning'),
    ('bg-info', 'Info'),
)

BOOTSTRAP4_TEXT_COLOUR_CHOICES = (
    ('text-primary', 'Primary'),
    ('text-secondary', 'Secondary'),
    ('text-light', 'Light'),
    ('text-dark', 'Dark'),
    ('text-white', 'White'),
    ('text-body', 'Body'),
    ('text-muted', 'Muted'),
    ('text-white-50', 'White-50'),
    ('text-black-50', 'Black-50'),
    ('text-success', 'Success'),
    ('text-danger', 'Danger'),
    ('text-warning', 'Warning'),
    ('text-info', 'Info'),
)

BOOTSTRAP4_BORDER_COLOUR_CHOICES = (
    ('', 'No Border'),
    ('border border-primary', 'Primary'),
    ('border border-secondary', 'Secondary'),
    ('border border-light', 'Light'),
    ('border border-dark', 'Dark'),
    ('border border-white', 'White'),
    ('border border-success', 'Success'),
    ('border border-danger', 'Danger'),
    ('border border-warning', 'Warning'),
    ('border border-info', 'Info'),
)

BOOTSTRAP4_UNIT_CHOICES = (
    ('rem', 'REM'),
    ('em', 'EM'),
    ('px', 'PX'),
)

BOOTSTRAP4_BUTTON_COLOUR_CHOICES = (
    ('btn btn-primary', 'Primary'),
    ('btn btn-secondary', 'Secondary'),
    ('btn btn-light', 'Light'),
    ('btn btn-dark', 'Dark'),
    ('btn btn-link', 'Link'),
    ('btn btn-success', 'Success'),
    ('btn btn-danger', 'Danger'),
    ('btn btn-warning', 'Warning'),
    ('btn btn-info', 'Info'),
    ('btn btn-outline-primary', 'Outline Primary'),
    ('btn btn-outline-secondary', 'Outline Secondary'),
    ('btn btn-outline-light', 'Outline Light'),
    ('btn btn-outline-dark', 'Outline Dark'),
    ('btn btn-outline-success', 'Outline Success'),
    ('btn btn-outline-danger', 'Outline Danger'),
    ('btn btn-outline-warning', 'Outline Warning'),
    ('btn btn-outline-info', 'Outline Info'),
)

BOOTSTRAP4_BUTTON_SIZE_CHOICES = (
    ('', 'Normal'),
    ('btn-sm', 'Small'),
    ('btn-lg', 'Large'),
)

BOOTSTRAP4_TWOCOL_RATIO_CHOICES = (
    ('1:1', '1:1'),
    ('2:1', '2:1'),
    ('1:2', '1:2'),
    ('3:1', '3:1'),
    ('1:3', '1:3'),
)

INSET_STYLE_CLASS_CHOICES = (
    ('container inset inset-raised', 'Standard Raised Inset'),
    ('container-fluid inset inset-raised', 'Wide Raised Inset'),
)

# these are sorted alphabetically in the settings model 
WAGTAIL_CODE_BLOCK_THEME_CHOICES = [

    ('default', 'Default'),
    ('coy', 'Coy'),
    ('dark', 'Dark'),
    ('funky', 'Funky'),
    ('okaidia', 'Okaidia'),
    ('solarizedlight', 'Solarized Light'),
    ('twilight', 'Twilight'),
    ('darcula', 'Darcula'),
    ('xonokai', 'Xonokai'),
    ('atom-dark', 'Atom Dark'),
    ('duotone-dark', 'Duotone Dark'),
    ('duotone-light', 'Duotone Light'),
    ('synthwave84', 'Synthwave \'84'),
    ('vs', 'Visual Studio'),
    ('vsc-dark', 'Visual Studio Code Dark'),

]





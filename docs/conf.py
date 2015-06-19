"""documentation config"""

from os.path import dirname, abspath
import sys
sys.path.insert(0, '{}'.format(dirname(dirname(abspath(__file__)))))
__version__ = '0.0.7'

try:
    import sphinx_bootstrap_theme
except ImportError as e:
    pass

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'documentation'
copyright = '2015, Daniel Mizyrycki'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
version = __version__
release = __version__

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

extensions = ['sphinx.ext.doctest']

try:
    import rst2pd  # noqa
    extensions += ['rst2pdf.pdfbuilder']
except ImportError as e:
    pass

pdf_documents = [('index', 'loadconfig', 'loadconfig docs',
    'Daniel Mizyrycki')]

# Use bootstrap theme if available. Assumed readthedocs otherwise
if 'sphinx_bootstrap_theme' in locals():
    html_theme = 'bootstrap'
    html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
    html_theme_options = {
        'globaltoc_depth': 3,
        'bootswatch_theme': "flatly"}

# Output file base name for HTML help builder.
htmlhelp_basename = 'documentation'

templates_path = ['_templates']

html_sidebars = {
    '*': ['sidebartoc.html', 'searchbox.html']}

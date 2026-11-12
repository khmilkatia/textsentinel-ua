"""textsentinel — перевірка якості тексту."""
__version__ = "0.1.0"

from .models import Issue
from .report import analyze

__all__ = ["Issue", "analyze", "__version__"]

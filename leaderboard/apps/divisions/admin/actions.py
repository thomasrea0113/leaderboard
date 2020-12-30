
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.db.models.query import QuerySet
    from . import ScoreAdmin
    from ..models import Score


def approve_score(_1: 'ScoreAdmin', _2: 'HttpRequest',
                  queryset: 'QuerySet[Score]'):
    queryset.update(approved=True)


approve_score.short_description = 'Approve selected scores'

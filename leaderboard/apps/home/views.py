from typing import TYPE_CHECKING
from django.db.models.expressions import F
from apps.home.query import pick
from apps.divisions.models import AgeDivision, Board, WeightClass
from apps.home.mixins import AjaxMixin, InitialTemplateView

if TYPE_CHECKING:
    from django.http import HttpRequest


class Index(AjaxMixin, InitialTemplateView):
    initial_template = "home/includes/index.html"

    def get_initial_context(self, request: 'HttpRequest', *args, **kwargs):
        boards = Board.objects.filter(featured=True)

        def gen(board: 'Board'):
            picked = pick(board, ('weight_class', WeightClass.__str__),
                          ('division', AgeDivision.__str__), name='board_definition__name')
            return {
                'board': picked,
                'socres': board.score_set.all().values('value', username=F('user__username'))
            }

        data = list(map(gen, boards))

        return super().get_initial_context(request, data=data)

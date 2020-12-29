from typing import TYPE_CHECKING, cast
import random
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager, AbstractBaseUser
from apps.divisions.models import Board, Score
from django.db.utils import IntegrityError
from . import seed

User = get_user_model()

if TYPE_CHECKING:
    from typing import Any, Optional


class Command(seed.Command):
    def handle(self, *args: 'Any', **options: 'Any') -> 'Optional[str]':
        super().handle(*args, **options)
        manager = cast(UserManager[AbstractBaseUser], User.objects)

        for user_number in range(0, 25):
            try:
                manager.create_user(
                    username=f'test-user-{user_number}',
                    email=f'test-user-{user_number}@gmail.com',
                    password='Password123')
            except IntegrityError:
                pass

        boards = [v[0] for v in Board.objects.all().values_list('id')]
        users = [v[0] for v in User.objects.all().values_list('id')]
        possible_scores = [round(v*.01, 2) for v in range(5000, 40000)]

        def yield_scores():
            for score_id in range(1, 100000):
                # explicility set id so that subsequent seeds don't add another 100000 scores
                yield Score(id=score_id, board_id=random.choice(boards),
                            user_id=random.choice(users), value=random.choice(possible_scores))

        Score.objects.bulk_create(
            yield_scores(), batch_size=10000, ignore_conflicts=True)

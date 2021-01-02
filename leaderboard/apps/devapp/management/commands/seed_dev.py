
from typing import TYPE_CHECKING, cast
import random
from itertools import product
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager, AbstractBaseUser
from django.core.management.base import CommandParser

from apps.users.models import Genders
from apps.divisions.models import AgeDivision, Board, Score, WeightClass
from apps.home.management.commands import seed

User = get_user_model()

if TYPE_CHECKING:
    from typing import Any, Optional


def date_between(start: 'date', end: 'date'):
    delta = end - start
    random_second = random.randrange(int(delta.total_seconds()))
    return start + timedelta(seconds=random_second)


def random_chance(probability: 'float') -> bool:
    return random.randint(0, 100) * .01 <= probability


class Command(seed.Command):
    def add_arguments(self, parser: 'CommandParser') -> None:
        super().add_arguments(parser)
        parser.add_argument(
            '--reset-passwords', action='store_true', help='Force a reset of all user passwords to the default')

    def handle(self, *args: 'Any', **options: 'Any') -> 'Optional[str]':
        super().handle(*args, **options)
        manager = cast(UserManager[AbstractBaseUser], User.objects)

        def yield_weight_classes():
            for gender in Genders.values:
                yield WeightClass(lower_bound=0, upper_bound=0, gender=gender)

        WeightClass.objects.bulk_create(
            yield_weight_classes(), ignore_conflicts=True)

        AgeDivision.objects.update_or_create(name='Any', defaults={
            'name': 'Any',
            'lower_bound': 0,
            'upper_bound': 0
        })

        for user_number in range(0, 100):
            gender = random.choice(Genders.values)

            user_args: 'dict[str, Any]' = {'username': f'test-user-{user_number}',
                                           'gender': gender}

            if random_chance(.5):
                user_args.update(email=f'test-user-{user_number}@gmail.com')

            if random_chance(.5):
                user_args.update(first_name=f'first{user_number}')

            if random_chance(.5):
                user_args.update(last_name=f'last{user_number}')

            if random_chance(.85):
                if gender == Genders.MALE.value:
                    weight = random.randint(5000, 12500) * .01
                else:
                    weight = random.randint(4000, 9000) * .01

                user_args.update(weight=round(weight, 2))

            if random_chance(.85):
                start = date.today() - relativedelta(years=81)
                end = date.today() - relativedelta(years=7)
                birthday = date_between(start, end)
                user_args.update(birthday=birthday)

            user, created = manager.update_or_create(
                username=user_args['username'], defaults=user_args)
            if created or options['reset_passwords']:
                user.set_password('Password123')
                user.save()

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

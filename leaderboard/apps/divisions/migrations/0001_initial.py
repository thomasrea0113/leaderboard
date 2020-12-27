# Generated by Django 3.1.4 on 2020-12-27 02:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AgeDivision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('lower_bound', models.PositiveIntegerField(default=0)),
                ('upper_bound', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='BoardDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('unit_type', models.CharField(choices=[('D', 'Distance'), ('P', 'Points'), ('T', 'Time'), ('W', 'Weight')], max_length=1)),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='WeightClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female')], max_length=1)),
                ('lower_bound', models.PositiveIntegerField(default=0)),
                ('upper_bound', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.AddConstraint(
            model_name='weightclass',
            constraint=models.CheckConstraint(check=models.Q(('lower_bound__lt', django.db.models.expressions.F('upper_bound')), ('upper_bound', 0), _connector='OR'), name='weight_range'),
        ),
        migrations.AddConstraint(
            model_name='weightclass',
            constraint=models.UniqueConstraint(fields=('lower_bound', 'upper_bound', 'gender'), name='unique_weight_class'),
        ),
        migrations.AddField(
            model_name='score',
            name='board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='divisions.board'),
        ),
        migrations.AddField(
            model_name='score',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='board',
            name='board_definition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='divisions.boarddefinition'),
        ),
        migrations.AddField(
            model_name='board',
            name='division',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='divisions.agedivision'),
        ),
        migrations.AddField(
            model_name='board',
            name='weight_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='divisions.weightclass'),
        ),
        migrations.AddConstraint(
            model_name='agedivision',
            constraint=models.CheckConstraint(check=models.Q(('lower_bound__lt', django.db.models.expressions.F('upper_bound')), ('upper_bound', 0), _connector='OR'), name='age_range'),
        ),
        migrations.AddConstraint(
            model_name='agedivision',
            constraint=models.UniqueConstraint(fields=('lower_bound', 'upper_bound'), name='unique_age_range'),
        ),
        migrations.AddConstraint(
            model_name='score',
            constraint=models.CheckConstraint(check=models.Q(value__gt=0), name='value_gt0'),
        ),
        migrations.AddConstraint(
            model_name='board',
            constraint=models.UniqueConstraint(fields=('board_definition', 'division', 'weight_class'), name='unique_board'),
        ),
    ]

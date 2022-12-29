from django.db import models
from core.settings import AUTH_USER_MODEL
from django.core.validators import MinValueValidator
from datetime import datetime, timedelta


ONCE = '0'
SECOND = '1'
MINUTE = '2'
HOUR = '3'
DAY = '4'
WEEK = '5'
MONTH = '6'
YEAR = '7'

RECURRENCE_UNIT_CHOICES = (
    (ONCE, 'once'),
    (SECOND, 'second'),
    (MINUTE, 'minute'),
    (HOUR, 'hour'),
    (DAY, 'day'),
    (WEEK, 'week'),
    (MONTH, 'month'),
    (YEAR, 'year'),
)

class PlanTag(models.Model):
    tag = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ('tag',)

    def __str__(self):
        return self.tag


class SubscriptionPlan(models.Model):
    plan_name = models.CharField(max_length=128)
    plan_description = models.CharField(blank=True,max_length=512,null=True)
    tags = models.ManyToManyField(PlanTag, blank=True, related_name='plans')
    'how many days after the subscription ends before the  subscription expires'
    grace_period = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('plan_name',)
        permissions = (
            ('subscriptions', 'Can interact with subscription details'),
        )

    def __str__(self):
        return self.plan_name

    def display_tags(self):

        if self.tags.count() > 3:
            return '{}, ...'.format(
                ', '.join(tag.tag for tag in self.tags.all()[:3])
            )
        return ', '.join(tag.tag for tag in self.tags.all()[:3])


class PlanCost(models.Model):
    """Cost and frequency of billing for a plan."""

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        related_name='costs',
    )

    slug = models.SlugField(
        blank=True,
        max_length=128,
        null=True,
        unique=True,
    )

    recurrence_period = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    recurrence_unit = models.CharField(
        choices=RECURRENCE_UNIT_CHOICES,
        default=MONTH,
        max_length=1,
    )

    cost = models.DecimalField(
        blank=True,
        decimal_places=4,
        max_digits=19,
        null=True,
    )

    def __str__(self):
        return str(self.plan)+' '+str(self.cost)


    class Meta:
        ordering = ('recurrence_unit', 'recurrence_period', 'cost',)

    @property
    def display_recurrent_unit_text(self):
        conversion = {
            ONCE: 'one-time',
            SECOND: 'per second',
            MINUTE: 'per minute',
            HOUR: 'per hour',
            DAY: 'per day',
            WEEK: 'per week',
            MONTH: 'per month',
            YEAR: 'per year',
        }
        return conversion[self.recurrence_unit]

    @property
    def display_billing_frequency_text(self):
        conversion = {
            ONCE: 'one-time',
            SECOND: {'singular': 'per second', 'plural': 'seconds'},
            MINUTE: {'singular': 'per minute', 'plural': 'minutes'},
            HOUR: {'singular': 'per hour', 'plural': 'hours'},
            DAY: {'singular': 'per day', 'plural': 'days'},
            WEEK: {'singular': 'per week', 'plural': 'weeks'},
            MONTH: {'singular': 'per month', 'plural': 'months'},
            YEAR: {'singular': 'per year', 'plural': 'years'},
        }

        if self.recurrence_unit == ONCE:
            return conversion[ONCE]

        if self.recurrence_period == 1:
            return conversion[self.recurrence_unit]['singular']

        return 'every {} {}'.format(
            self.recurrence_period, conversion[self.recurrence_unit]['plural']
        )

    def next_billing_datetime(self, current):

        if self.recurrence_unit == SECOND:
            delta = timedelta(seconds=self.recurrence_period)
        elif self.recurrence_unit == MINUTE:
            delta = timedelta(minutes=self.recurrence_period)
        elif self.recurrence_unit == HOUR:
            delta = timedelta(hours=self.recurrence_period)
        elif self.recurrence_unit == DAY:
            delta = timedelta(days=self.recurrence_period)
        elif self.recurrence_unit == WEEK:
            delta = timedelta(weeks=self.recurrence_period)
        elif self.recurrence_unit == MONTH:
            delta = timedelta(
                days=30.4368 * self.recurrence_period
            )
        elif self.recurrence_unit == YEAR:
            delta = timedelta(
                days=365.2425 * self.recurrence_period
            )
        else:
            return None
        return current + delta



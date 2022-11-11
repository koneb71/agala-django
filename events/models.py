from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.text import slugify

from app.models import BaseModel
from app.utils import generate_pin_code


class Event(BaseModel):
    STATUS = (
        ('published', 'Published'),
        ('draft', 'Draft')
    )

    name = models.CharField(
        max_length=120,
        null=False,
        blank=False,
        db_index=True,
        help_text='Name of the event. 40 Characters is advised limit.'
    )
    start = models.DateTimeField(
        verbose_name='Event Start Timings'
    )
    end = models.DateTimeField(
        verbose_name='Event End Timings'
    )
    description = models.TextField(
        verbose_name='Event Description',
    )
    remark = models.CharField(
        verbose_name='Special Remark for Users',
        max_length=255,
        null=True,
        blank=True
    )
    address = models.TextField(
        null=True,
        blank=True,
        verbose_name='Where',
        help_text='Enter address of the event'
    )
    slug = models.SlugField(
        max_length=500,
        null=True,
        blank=False,
        default=None,
        verbose_name='URL Handle',
        unique=True,
        help_text='Just put the location name here without /'
    )
    status = models.CharField(
        choices=STATUS,
        max_length=120,
        default='draft',
        null=False,
        blank=False
    )
    DEFAULT_GOOGLE_MAP_URL = 'https://www.google.com/maps'
    google_map_url = models.URLField(
        max_length=500,
        null=False,
        blank=False,
        default=DEFAULT_GOOGLE_MAP_URL,
        verbose_name='Google Map Link',
        help_text='Paste the google map url here'
    )
    pin_code = models.CharField(
        null=True,
        max_length=6,
        blank=True,
        unique=True,
        help_text='If you leave this field blank it will auto generate a PIN code.',
        validators=[MinLengthValidator(4, message='Must be 4 to 6 characters')]
    )

    class Meta:
        verbose_name = 'event'
        verbose_name_plural = 'events'
        ordering = ('start',)

    def clean(self):
        # End date must be greater or equal to start date.
        if self.start and self.end:
            if self.start > self.end:
                raise ValidationError('Start date should not be greater than end date.')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pin_code:
            pin_code = generate_pin_code()
            while Event.objects.filter(pin_code=pin_code).first():
                pin_code = generate_pin_code()
            self.pin_code = pin_code
        if not self.slug and self.name:
            slug = slugify(self.name)
            if self.start and Event.objects.filter(slug=slug).first():
                slug += '-' + self.start.strftime('%m%d%Y')
            self.slug = slug
        super(Event, self).save(*args, **kwargs)


class EventTicket(BaseModel):
    is_free = models.BooleanField(default=False, blank=False, null=False, verbose_name='This is Free Ticket')
    remaining_count = models.IntegerField()
    price = models.FloatField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    sales_start_date = models.DateField(null=True, blank=True, default=None,
                                        help_text='If this is empty it will use the event creation date')
    sales_end_date = models.DateField(null=True, blank=True, default=None)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.event} - {self.description}'

    def is_ticket_free(self):
        return self.is_free

    @property
    def event_name(self):
        return self.event.name


class TicketOrder(BaseModel):
    DELIVERY_STATUS = (
        ('pending', 'Pending'),
        ('delivered', 'Delivered')
    )
    total_price = models.FloatField()
    sent_ticket_to = models.EmailField(blank=False, null=False)
    contact_name = models.CharField(null=True, blank=False, max_length=120, verbose_name="Buyer's Name")
    contact_club = models.DateField(null=True, blank=False, verbose_name="Buyer's Club")
    contact_id = models.CharField(null=True, blank=False, max_length=200, verbose_name="Buyer's ID Card Number")
    contact_mobile = models.CharField(null=True, blank=False, max_length=80, verbose_name='Contact Number')
    order_num = models.CharField(null=True, blank=False, max_length=20)
    delivery_status = models.CharField(null=False, blank=False, max_length=80, choices=DELIVERY_STATUS, default='delivered')

    def order_id(self):
        return self.pk

    def __str__(self):
        return str(self.pk)


class TicketOrderDetail(BaseModel):
    order_id = models.ForeignKey(TicketOrder, on_delete=models.DO_NOTHING)
    ticket = models.ForeignKey(EventTicket, on_delete=models.DO_NOTHING)
    count = models.IntegerField()
    price = models.FloatField()

    def save(self,*args, **kwargs):
        self.ticket.remaining_count = self.ticket.remaining_count - self.count
        self.ticket.save()
        super(TicketOrderDetail, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket.event} - {self.order_id.order_num}"

    @property
    def event_name(self):
        return self.ticket.event


class TicketDetail(BaseModel):
    order_details = models.ForeignKey(TicketOrderDetail, on_delete=models.DO_NOTHING)
    name = models.CharField(null=False, blank=False, max_length=120)
    email = models.EmailField(null=True, blank=True, default=None)
    used = models.BooleanField(null=False, blank=False, default=False)
    contact_id = models.CharField(null=True, blank=True, max_length=200)
    mobile_num = models.CharField(null=True, blank=True, max_length=80)
    qrcode = models.URLField(null=True, blank=False)

    class Meta:
        verbose_name = 'Attendee Information'

    def __str__(self):
        return self.name

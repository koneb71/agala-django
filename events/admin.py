from django.contrib import admin

from events.models import Event, EventTicket, TicketOrder, TicketOrderDetail, TicketDetail


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'end', 'pin_code', 'status', 'updated_at', 'created_at')
    search_fields = list_display
    list_filter = ['name']
    ordering = ('-created_at',)
    readonly_fields = ('id',)


@admin.register(EventTicket)
class EventTicketAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'price', 'sales_start_date', 'sales_end_date', 'updated_at', 'created_at')
    search_fields = list_display
    ordering = ('-created_at',)
    readonly_fields = ('id',)


@admin.register(TicketOrder)
class TicketOrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_num', 'sent_ticket_to', 'total_price', 'contact_name', 'contact_club',
        'contact_id', 'contact_mobile', 'delivery_status', 'created_at'
    )
    search_fields = list_display
    list_filter = ['sent_ticket_to', 'contact_name']
    ordering = ('-created_at',)
    readonly_fields = ('id',)


@admin.register(TicketOrderDetail)
class TicketOrderDetailAdmin(admin.ModelAdmin):
    list_display = (
        'event_name', 'order_id', 'count', 'price'
    )
    search_fields = list_display
    ordering = ('-created_at',)
    readonly_fields = ('id',)


@admin.register(TicketDetail)
class TicketDetailAdmin(admin.ModelAdmin):
    list_display = (
         'name', 'order_details', 'email', 'contact_id', 'mobile_num', 'used'
    )
    search_fields = list_display
    list_filter = ['name']
    ordering = ('-created_at',)
    readonly_fields = ('id',)

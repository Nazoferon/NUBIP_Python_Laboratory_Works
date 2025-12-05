from django.contrib import admin
from .models import Books, Readers, Bookloans

@admin.register(Books)
class BooksAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'section', 'price')

@admin.register(Readers)
class ReadersAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'group_name', 'phone')

@admin.register(Bookloans)
class BookLoansAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'loan_date', 'reader_ticket_number', 'book_inventory_number')
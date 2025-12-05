from django.shortcuts import render
from .models import Books, Readers, Bookloans

def index(request):
    books = Books.objects.all()
    readers = Readers.objects.all()
    loans = Bookloans.objects.select_related('reader_ticket_number', 'book_inventory_number').all()
    
    context = {
        'student_name': 'Ганюк Назар Олександрович',
        'student_group': 'ІПЗ-23008бск',
        'books': books,
        'readers': readers,
        'loans': loans,
    }
    return render(request, 'catalog/index.html', context)
from django.db import models

class Books(models.Model):
    inventory_number = models.AutoField(primary_key=True)
    author = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    section = models.CharField(max_length=50, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    pages_count = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    copies_count = models.IntegerField(blank=True, null=True)
    max_loan_days = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False # Django не буде змінювати таблицю, бо вона створена app.py
        db_table = 'books'

    def __str__(self):
        return f"{self.title} ({self.author})"

class Readers(models.Model):
    reader_ticket_number = models.AutoField(primary_key=True)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    course = models.IntegerField(blank=True, null=True)
    group_name = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'readers'

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.group_name})"

class Bookloans(models.Model):
    loan_id = models.AutoField(primary_key=True)
    loan_date = models.DateField()
    # Django inspectdb зазвичай називає поля як reader_ticket_number, 
    # але ми вказуємо ForeignKey явно
    reader_ticket_number = models.ForeignKey(Readers, models.DO_NOTHING, db_column='reader_ticket_number')
    book_inventory_number = models.ForeignKey(Books, models.DO_NOTHING, db_column='book_inventory_number')

    class Meta:
        managed = False
        db_table = 'bookloans'
    
    def __str__(self):
        return f"Видача №{self.loan_id}"
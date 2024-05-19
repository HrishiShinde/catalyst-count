from django.db import models

# Create your models here.
class File(models.Model):
    existingPath = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=50)
    eof = models.BooleanField()

    class Meta:
        db_table = 'upload_file'

class Company(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    domain = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    year_founded = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    industry = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    size_range = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    city = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    state = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    country = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    linkedin_url = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    current_employee_estimate = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    total_employee_estimate = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    class Meta:
        db_table = 'company'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['domain']),
            models.Index(fields=['year_founded']),
            models.Index(fields=['industry']),
            models.Index(fields=['city']),
            models.Index(fields=['state']),
            models.Index(fields=['country']),
            models.Index(fields=['current_employee_estimate']),
            models.Index(fields=['total_employee_estimate']),
        ]

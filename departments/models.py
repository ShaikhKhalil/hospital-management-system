from django.db import models

class Department(models.Model):
    department_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.department_name

    class Meta:
        verbose_name_plural = "Departments"
from django.contrib import admin
from .models import Refugio, Centro, Vacuna, Animal, RevisionVeterinaria, AnimalVacunas

# Register your models here.

admin.site.register(Refugio)
admin.site.register(Centro)
admin.site.register(Vacuna)
admin.site.register(Animal)
admin.site.register(RevisionVeterinaria)
admin.site.register(AnimalVacunas)
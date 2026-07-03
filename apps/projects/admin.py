from django.contrib import admin
from .models import Project, ProjectImage, ProjectPhase, Amenity

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'status', 'featured', 'total_plots']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    pass

@admin.register(ProjectPhase)
class ProjectPhaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'total_plots', 'order']

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    pass

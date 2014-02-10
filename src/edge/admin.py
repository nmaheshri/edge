from django.contrib import admin
from edge.models import Genome, Fragment


class Genome_Admin(admin.ModelAdmin):
    list_display = ('id', 'name', 'notes', 'parent', 'created_on')
    search_fields = ('name',)
    fields = ('name', 'notes')
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def delete_model(self, request, obj):
        raise Exception("Not allowed")

admin.site.register(Genome, Genome_Admin)


class Fragment_Admin(admin.ModelAdmin):
    list_display = ('id', 'name', 'circular', 'parent', 'created_on')
    search_fields = ('name',)
    fields = ('name', 'circular')
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def delete_model(self, request, obj):
        raise Exception("Not allowed")

admin.site.register(Fragment, Fragment_Admin)
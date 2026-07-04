from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.plots.models import Plot
from apps.projects.models import Project


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'website:home',
            'website:about',
            'website:contact',
            'website:faq',
            'website:hire_purchase',
            'website:blog',
            'website:testimonials',
            'plots:plot_list',
            'projects:project_list',
        ]

    def location(self, item):
        return reverse(item)


class PlotSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Plot.objects.filter(status='available').select_related('project')

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else None

    def location(self, obj):
        return reverse('plots:plot_detail', args=[obj.pk])


class ProjectSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Project.objects.all()

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else None

    def location(self, obj):
        return reverse('projects:project_detail', args=[obj.slug])

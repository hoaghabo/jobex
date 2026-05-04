from django.contrib import admin

from apps.crm.customer.Jobseeker.jobseeker_profile.models import JobSeekerProfile


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in JobSeekerProfile._meta.fields]

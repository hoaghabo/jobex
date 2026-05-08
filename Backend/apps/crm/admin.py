from django.contrib import admin

from apps.crm.customer.Jobseeker.jobseeker_profile.models import JobSeekerProfile
from apps.crm.customer.company.company_profile.models import CompanyProfile
from apps.crm.customer.company.job_posts.models import JobPosting


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in JobSeekerProfile._meta.fields]
    
@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CompanyProfile._meta.fields]
    
@admin.register(JobPosting)
class CompanyJobpostAdmin(admin.ModelAdmin):
    list_display = [field.name for field in JobPosting._meta.fields]    


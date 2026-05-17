from django.contrib import admin

from apps.crm.customer.Jobseeker.jobseeker_profile.models import JobSeekerProfile
from apps.crm.customer.company.company_profile.models import CompanyProfile
from apps.crm.customer.company.job_posts.models import JobPosting
from apps.crm.customer.Jobseeker.jobs_application.models import CampaignChannel , JobSeekerProfileCampaignChannel
from apps.crm.customer.company.company_membership.models import CompanyMembership , CompanyRole

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in JobSeekerProfile._meta.fields]
    
@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CompanyProfile._meta.fields]
    
@admin.register(JobPosting)
class CompanyJobpostAdmin(admin.ModelAdmin):
    list_display = [field.name for field in JobPosting._meta.fields]    

@admin.register(CampaignChannel)
class JobseekerCampaginAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CampaignChannel._meta.fields]    

@admin.register(JobSeekerProfileCampaignChannel)
class JobseekerCampaginAskAdmin(admin.ModelAdmin):
    list_display = [field.name for field in JobSeekerProfileCampaignChannel._meta.fields]    

@admin.register(CompanyMembership)
class CompanyMembershipAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CompanyMembership._meta.fields]    



@admin.register(CompanyRole)
class CompanyMembershipRoleAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CompanyRole._meta.fields]    
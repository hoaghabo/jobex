from django.apps import AppConfig

class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.crm'
    
    def ready(self):
        # import apps.crm.signals 
        # import apps.crm.customer.company.company_profile.signals
        import apps.crm.customer.Jobseeker.jobseeker_profile.signals

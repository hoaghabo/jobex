from django.core.management.base import BaseCommand

from apps.billing.models import (
    ProductCategory,
    ProductType,
    ProductStatus,
    Product,
)


class Command(BaseCommand):
    help = "Seed test data for billing product categories, product types, product statuses and products"

    def handle(self, *args, **options):
        self.seed_product_statuses()
        self.seed_product_types()
        self.seed_product_categories()
        self.seed_products()

        self.stdout.write(
            self.style.SUCCESS("Billing test data seeded successfully.")
        )

    def seed_product_statuses(self):
        statuses = [
            {
                "title": "فعال",
                "code": "active",
                "description": "محصول فعال و قابل نمایش",
                "is_active": True,
                "sort_order": 1,
            },
            {
                "title": "غیرفعال",
                "code": "inactive",
                "description": "محصول غیرفعال و غیرقابل نمایش",
                "is_active": True,
                "sort_order": 2,
            },
            {
                "title": "پیش‌نویس",
                "code": "draft",
                "description": "محصول در حالت پیش‌نویس",
                "is_active": True,
                "sort_order": 3,
            },
            {
                "title": "آرشیو شده",
                "code": "archived",
                "description": "محصول آرشیو شده",
                "is_active": True,
                "sort_order": 4,
            },
        ]

        for item in statuses:
            obj, created = ProductStatus.objects.update_or_create(
                code=item["code"],
                defaults={
                    "title": item["title"],
                    "description": item["description"],
                    "is_active": item["is_active"],
                    "sort_order": item["sort_order"],
                },
            )

            action = "created" if created else "updated"
            self.stdout.write(f"ProductStatus {action}: {obj.title}")

    def seed_product_types(self):
        types = [
            {
                "title": "پکیج کارجو",
                "code": "job_seeker_package",
                "description": "محصولات و پکیج‌های مخصوص کارجویان",
                "is_active": True,
                "requires_fulfillment": False,
                "sort_order": 1,
            },
            {
                "title": "پکیج کارفرما",
                "code": "employer_package",
                "description": "محصولات و پکیج‌های مخصوص کارفرمایان",
                "is_active": True,
                "requires_fulfillment": False,
                "sort_order": 2,
            },
            {
                "title": "سرویس عمومی",
                "code": "general_service",
                "description": "سرویس‌های عمومی",
                "is_active": True,
                "requires_fulfillment": False,
                "sort_order": 3,
            },
        ]

        for item in types:
            obj, created = ProductType.objects.update_or_create(
                code=item["code"],
                defaults={
                    "title": item["title"],
                    "description": item["description"],
                    "is_active": item["is_active"],
                    "requires_fulfillment": item["requires_fulfillment"],
                    "sort_order": item["sort_order"],
                },
            )

            action = "created" if created else "updated"
            self.stdout.write(f"ProductType {action}: {obj.title}")

    def seed_product_categories(self):
        categories = [
            {
                "title": "کارجو",
                "slug": "job-seeker",
                "description": "دسته‌بندی محصولات مخصوص کارجویان",
                "is_active": True,
                "sort_order": 1,
                "children": [
                    {
                        "title": "رزومه و پروفایل",
                        "slug": "resume-and-profile",
                        "description": "سرویس‌های مربوط به رزومه و پروفایل",
                        "is_active": True,
                        "sort_order": 1,
                    },
                    {
                        "title": "آمادگی مصاحبه",
                        "slug": "interview-preparation",
                        "description": "سرویس‌های مربوط به آمادگی مصاحبه",
                        "is_active": True,
                        "sort_order": 2,
                    },
                    {
                        "title": "ارتقای شغلی",
                        "slug": "career-growth",
                        "description": "سرویس‌های مربوط به توسعه مسیر شغلی",
                        "is_active": True,
                        "sort_order": 3,
                    },
                ],
            },
            {
                "title": "کارفرما",
                "slug": "employer",
                "description": "دسته‌بندی محصولات مخصوص کارفرمایان",
                "is_active": True,
                "sort_order": 2,
                "children": [
                    {
                        "title": "ثبت آگهی شغلی",
                        "slug": "job-posting",
                        "description": "سرویس‌های ثبت آگهی",
                        "is_active": True,
                        "sort_order": 1,
                    },
                    {
                        "title": "جستجوی رزومه",
                        "slug": "resume-search",
                        "description": "سرویس‌های جستجو و مشاهده رزومه",
                        "is_active": True,
                        "sort_order": 2,
                    },
                    {
                        "title": "برندسازی کارفرمایی",
                        "slug": "employer-branding",
                        "description": "سرویس‌های برندینگ کارفرما",
                        "is_active": True,
                        "sort_order": 3,
                    },
                ],
            },
            {
                "title": "عمومی",
                "slug": "general",
                "description": "محصولات عمومی",
                "is_active": True,
                "sort_order": 3,
                "children": [
                    {
                        "title": "مشاوره",
                        "slug": "consulting",
                        "description": "سرویس‌های مشاوره",
                        "is_active": True,
                        "sort_order": 1,
                    },
                    {
                        "title": "آموزش",
                        "slug": "education",
                        "description": "سرویس‌های آموزشی",
                        "is_active": True,
                        "sort_order": 2,
                    },
                ],
            },
        ]

        for item in categories:
            parent, created = ProductCategory.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "description": item["description"],
                    "is_active": item["is_active"],
                    "sort_order": item["sort_order"],
                    "parent": None,
                },
            )

            action = "created" if created else "updated"
            self.stdout.write(f"ProductCategory {action}: {parent.title}")

            for child_item in item["children"]:
                child, child_created = ProductCategory.objects.update_or_create(
                    slug=child_item["slug"],
                    defaults={
                        "title": child_item["title"],
                        "description": child_item["description"],
                        "is_active": child_item["is_active"],
                        "sort_order": child_item["sort_order"],
                        "parent": parent,
                    },
                )

                child_action = "created" if child_created else "updated"
                self.stdout.write(
                    f"ProductCategory {child_action}: {parent.title} > {child.title}"
                )

    def seed_products(self):
        active_status = ProductStatus.objects.get(code="active")

        job_seeker_type = ProductType.objects.get(code="job_seeker_package")
        employer_type = ProductType.objects.get(code="employer_package")
        general_type = ProductType.objects.get(code="general_service")

        resume_category = ProductCategory.objects.get(slug="resume-and-profile")
        interview_category = ProductCategory.objects.get(slug="interview-preparation")
        career_category = ProductCategory.objects.get(slug="career-growth")

        posting_category = ProductCategory.objects.get(slug="job-posting")
        search_category = ProductCategory.objects.get(slug="resume-search")
        branding_category = ProductCategory.objects.get(slug="employer-branding")

        consulting_category = ProductCategory.objects.get(slug="consulting")
        education_category = ProductCategory.objects.get(slug="education")

        products = [
            {
                "title": "پکیج ساخت رزومه حرفه‌ای",
                "slug": "professional-resume-package",
                "sku": "PRD-001",
                "short_description": "ساخت و بهینه‌سازی رزومه برای کارجویان",
                "description": "این پکیج شامل بررسی رزومه، بازنویسی حرفه‌ای و بهینه‌سازی برای موقعیت‌های شغلی است.",
                "base_price": 490000,
                "category": resume_category,
                "product_type": job_seeker_type,
                "status": active_status,
                "is_active": True,
                "is_public": True,
                "sort_order": 1,
            },
            {
                "title": "پکیج آمادگی مصاحبه",
                "slug": "interview-preparation-package",
                "sku": "PRD-002",
                "short_description": "آموزش و شبیه‌سازی مصاحبه شغلی",
                "description": "این محصول برای آمادگی بهتر در مصاحبه‌های شغلی طراحی شده است.",
                "base_price": 650000,
                "category": interview_category,
                "product_type": job_seeker_type,
                "status": active_status,
                "is_active": True,
                "is_public": True,
                "sort_order": 2,
            },
            {
                "title": "پکیج ارتقای مسیر شغلی",
                "slug": "career-growth-package",
                "sku": "PRD-003",
                "short_description": "تحلیل مسیر شغلی و برنامه‌ریزی رشد",
                "description": "این محصول به کارجو کمک می‌کند برای رشد شغلی خود برنامه‌ریزی دقیق‌تری داشته باشد.",
                "base_price": 790000,
                "category": career_category,
                "product_type": job_seeker_type,
                "status": active_status,
                "is_active": True,
                "is_public": True,
                "sort_order": 3,
            },
            {
                "title": "پکیج ثبت آگهی شغلی",
                "slug": "job-posting-package",
                "sku": "PRD-004",
                "short_description": "انتشار آگهی استخدام برای کارفرمایان",
                "description": "این پکیج برای ثبت و انتشار آگهی‌های شغلی استفاده می‌شود.",
                "base_price": 1200000,
                "category": posting_category,
                "product_type": employer_type,
                "status": active_status,
                "is_active": True,
                "is_public": True,
                "sort_order": 4,
            },
            {
                "title": "پکیج جستجوی رزومه",
                "slug": "resume-search-package",
                "sku": "PRD-005",
                "short_description": "دسترسی به بانک رزومه کارجویان",
                "description": "این محصول دسترسی کارفرما به رزومه‌های منتخب را فراهم می‌کند.",
                "base_price": 1800000,
                "category": search_category,
                "product_type": employer_type,
                "status": active_status,
                "is_active": True,
                "is_public": True,
                "sort_order": 5,
            },
            {
                "title": "پکیج برندسازی کارفرمایی",
                "slug": "employer-branding-package",
                "sku": "PRD-006",
                "short_description": "تقویت برند کارفرما در پلتفرم",
                "description": "این پکیج برای معرفی بهتر برند کارفرما و جذب نیروی مناسب است.",
                "base_price": 2500000,
                "category": branding_category,
                "product_type": employer_type,
                "status": active_status,
                "is_active": True,
                "is_public": True,
                "sort_order": 6,
            },
            {
                "title": "جلسه مشاوره شغلی",
                "slug": "career-consulting-session",
                "sku": "PRD-007",
                "short_description": "مشاوره تخصصی برای مسیر شغلی",
                "description": "جلسه مشاوره برای انتخاب مسیر شغلی و تصمیم‌گیری بهتر.",
                "base_price": 350000,
                "category": consulting_category,
                "product_type": general_type,
                "status": active_status,
                "is_active": True,
                "is_public": True,
                "sort_order": 7,
            },
            {
                "title": "دوره آموزشی منابع انسانی",
                "slug": "human-resources-training-course",
                "sku": "PRD-008",
                "short_description": "آموزش اصول منابع انسانی",
                "description": "دوره آموزشی مناسب برای علاقه‌مندان و فعالان حوزه منابع انسانی.",
                "base_price": 950000,
                "category": education_category,
                "product_type": general_type,
                "status": active_status,
                "is_active": True,
                "is_public": True,
                "sort_order": 8,
            },
        ]

        for item in products:
            obj, created = Product.objects.update_or_create(
                sku=item["sku"],
                defaults={
                    "title": item["title"],
                    "slug": item["slug"],
                    "short_description": item["short_description"],
                    "description": item["description"],
                    "base_price": item["base_price"],
                    "category": item["category"],
                    "product_type": item["product_type"],
                    "status": item["status"],
                    "is_active": item["is_active"],
                    "is_public": item["is_public"],
                    "sort_order": item["sort_order"],
                },
            )

            action = "created" if created else "updated"
            self.stdout.write(f"Product {action}: {obj.title}")

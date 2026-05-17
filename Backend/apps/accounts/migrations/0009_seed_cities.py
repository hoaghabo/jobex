from django.db import migrations


def create_default_cities(apps, schema_editor):
    City = apps.get_model("accounts", "City")

    cities = [
        {"slug": "tehran", "name": "تهران"},
        {"slug": "alborz", "name": "البرز"},
        {"slug": "yazd", "name": "یزد"},
        {"slug": "ahvaz", "name": "اهواز"},
        {"slug": "mazandaran", "name": "مازندران"},
        {"slug": "kerman", "name": "کرمان"},
        {"slug": "mashhad", "name": "مشهد"},
        {"slug": "gilan", "name": "گیلان"},
        {"slug": "shiraz", "name": "شیراز"},
        {"slug": "tabriz", "name": "تبریز"},
        {"slug": "qazvin", "name": "قزوین"},
        {"slug": "other", "name": "سایر"},
    ]

    for city in cities:
        City.objects.get_or_create(
            slug=city["slug"],
            defaults={"name": city["name"]},
        )


def remove_default_cities(apps, schema_editor):
    City = apps.get_model("accounts", "City")
    slugs = [
        "tehran",
        "alborz",
        "yazd",
        "ahvaz",
        "mazandaran",
        "kerman",
        "mashhad",
        "gilan",
        "shiraz",
        "tabriz",
        "qazvin",
        "other",
    ]
    City.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_city_remove_accounts_username_and_more"),
    ]

    operations = [
        migrations.RunPython(create_default_cities, remove_default_cities),
    ]

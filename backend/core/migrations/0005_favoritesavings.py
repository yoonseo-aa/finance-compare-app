from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0004_favoriteloan"),
    ]

    operations = [
        migrations.CreateModel(
            name="FavoriteSavings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_code", models.CharField(max_length=160)),
                ("product_type_label", models.CharField(blank=True, max_length=40)),
                ("product_subtype", models.CharField(blank=True, max_length=80)),
                ("name", models.CharField(max_length=200)),
                ("bank_name", models.CharField(max_length=100)),
                ("rate_value", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ("rate_label", models.CharField(blank=True, max_length=40)),
                ("join_way", models.CharField(blank=True, max_length=200)),
                ("join_member", models.CharField(blank=True, max_length=200)),
                ("special_condition", models.TextField(blank=True)),
                ("etc_note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="joined_savings", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("user", "product_code")},
            },
        ),
    ]

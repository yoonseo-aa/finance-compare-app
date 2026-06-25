from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0003_user_age_group_user_asset_level_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="FavoriteLoan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("loan_type", models.CharField(choices=[("mortgage", "주택담보대출"), ("rent", "전세자금대출"), ("credit", "개인신용대출")], max_length=20)),
                ("product_code", models.CharField(max_length=80)),
                ("name", models.CharField(max_length=200)),
                ("bank_name", models.CharField(max_length=100)),
                ("loan_type_label", models.CharField(blank=True, max_length=40)),
                ("rate_min", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ("loan_limit", models.CharField(blank=True, max_length=200)),
                ("repay_type", models.CharField(blank=True, max_length=200)),
                ("join_member", models.CharField(blank=True, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="joined_loans", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("user", "loan_type", "product_code")},
            },
        ),
    ]

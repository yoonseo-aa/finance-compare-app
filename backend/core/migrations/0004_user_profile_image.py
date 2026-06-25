from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_user_age_group_user_asset_level_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="profile_image",
            field=models.FileField(blank=True, null=True, upload_to="profiles/"),
        ),
    ]

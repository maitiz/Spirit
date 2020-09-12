# Generated by Django 3.0.7 on 2020-09-11 17:59

from django.db import migrations, models
import spirit.core.utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskResultModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='autoslugbadpopulatefrommodel',
            name='slug',
            field=spirit.core.utils.models.AutoSlugField(allow_unicode=True, populate_from='bad'),
        ),
        migrations.AlterField(
            model_name='autoslugdefaultmodel',
            name='slug',
            field=spirit.core.utils.models.AutoSlugField(allow_unicode=True, default='foo'),
        ),
        migrations.AlterField(
            model_name='autoslugpopulatefrommodel',
            name='slug',
            field=spirit.core.utils.models.AutoSlugField(allow_unicode=True, populate_from='title'),
        ),
    ]
# Generated by Django 4.2.5 on 2023-09-30 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_commerce_app', '0004_rename_products_order_items_alter_item_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/images/')),
            ],
            options={
                'db_table': 'item_image',
            },
        ),
        migrations.RemoveField(
            model_name='item',
            name='image',
        ),
        migrations.AlterModelTable(
            name='item',
            table='item',
        ),
        migrations.AddField(
            model_name='item',
            name='images',
            field=models.ManyToManyField(to='e_commerce_app.itemimage'),
        ),
    ]

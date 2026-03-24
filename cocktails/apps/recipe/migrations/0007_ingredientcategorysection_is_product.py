from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0006_remove_ingredient_subcategory_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredientcategorysection',
            name='is_product',
            field=models.BooleanField(
                default=False,
                verbose_name='Раздел "Продукты"?',
                help_text='True для разделов типа "Продукты" (не напитки). Нужно для корректной фильтрации в приложении.'
            ),
        ),
    ]

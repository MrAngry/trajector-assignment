from tortoise import Model, fields
from tortoise.fields import SET_NULL, ForeignKeyNullableRelation

from models.tag import Tag


class Item(Model):
    # We simplify the field type from UUID to int for the sake of easier testing of this assignment
    id = fields.IntField(pk=True, generated=True)

    next: ForeignKeyNullableRelation["Item"] = fields.ForeignKeyField('models.Item',
                                                                      related_name=False,
                                                                      to_field="id", on_delete=SET_NULL, null=True)
    previous: ForeignKeyNullableRelation["Item"] = fields.ForeignKeyField('models.Item',
                                                                          related_name=False,
                                                                          to_field="id", on_delete=SET_NULL, null=True)

    url = fields.CharField(index=True, max_length=2048)
    thumbnail = fields.CharField(max_length=2048, null=True)
    tags: fields.ManyToManyRelation["Tag"] = fields.ManyToManyField("models.Tag")

    price = fields.DecimalField(max_digits=10, decimal_places=2)
    is_favorite = fields.BooleanField(default=False)
    quantity = fields.IntField(default=1)

    class PydanticMeta:
        exclude_raw_fields = False

    # TODO override delete method to remove stale thumbnails



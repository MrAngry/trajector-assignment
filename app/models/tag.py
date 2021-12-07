from tortoise import Model, fields


class Tag(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=20, unique=True, index=True)
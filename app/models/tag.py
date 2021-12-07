from tortoise import Model, fields


class Tag(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=20, unique=True, index=True)
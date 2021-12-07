from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

from models.item import Item


class DoublyLinkedList():
    def __init__(self, first_element_id: int = None):
        self.first_element_id = first_element_id
        self.items = []
        self.initialized = False
        self.first_item = None

    async def init(self):
        """
         Initialize linked list by loading first element
        """
        try:
            if self.first_element_id is None:
                self.first_item = (await Item.get(previous=None))
            else:
                self.first_item = (await Item.get(pk=self.first_element_id))
        except DoesNotExist:
            pass
        self.initialized = True

    async def fetch(self):
        """
        Utility function to allow fetching the whole linked list  in a single query from DB only available in postgreSQL

        """

        await self.init()
        if not self.first_item:
            return []

        query = f'''
            WITH RECURSIVE cte_query 
        AS 
        (
        select item.id, item.next_id
        from item 
        where item.id = {self.first_element_id} 
        UNION ALL
        select item.id, item.next_id
        From item
        INNER JOIN cte_query c ON c.next_id = item.id
        )
        Select * from cte_query;
            '''
        conn = Tortoise.get_connection("default")
        result = await conn.execute_query(query)

        self.items = await Item.filter(pk__in=[entry['id'] for entry in result[1]]).prefetch_related("tags")

    async def add(self, item: Item):
        if not item.previous_id and not item.next_id:
            await self.insert_first(item)
        elif item.previous_id:
            await self.insert_after(item)
        elif item.next_id:
            await self.insert_before(item)

    async def insert_first(self, item: Item):
        if self.first_item:
            item.next_id = self.first_item.id
            self.first_item.previous_id = item.id
            await self.first_item.save(update_fields=['previous_id', ])
        await item.save()

    async def insert_after(self, new_item: Item):
        previous_item = await Item.get(pk=new_item.previous_id).prefetch_related("next")
        next_item = previous_item.next

        new_item.next_id = previous_item.next_id
        previous_item.next_id = new_item.id

        next_item.previous_id = new_item.id

        await Item.bulk_update(objects=(previous_item, new_item, next_item), fields=('next_id', 'previous_id'))
        return

    async def insert_before(self, new_item: Item):
        next_item = await Item.get(pk=new_item.next_id).prefetch_related("previous")
        previous_item = next_item.previous

        new_item.previous_id = next_item.previous_id
        next_item.previous_id = new_item.id

        previous_item.next_id = new_item.id

        await Item.bulk_update(objects=(previous_item, new_item, next_item), fields=('next_id', 'previous_id'))
        return

    async def remove_item(self, item: Item):
        next_item = item.next
        previous_item = item.previous

        # In other cases DB will SET NULL for us
        if previous_item and next_item:
            previous_item.next = next_item
            next_item.previous = previous_item
            await Item.bulk_update(objects=(previous_item, next_item), fields=('next_id', 'previous_id'))
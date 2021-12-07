import re
from typing import List

import requests
from fastapi import APIRouter, Query
from starlette.background import BackgroundTasks
from tortoise.transactions import in_transaction

from config import settings
from models.doubly_linked_list import DoublyLinkedList
from models.item import Item
from models.tag import Tag
from schemas.item import ItemOut, ItemCreate, ItemOutWithTagsSerialized, ItemPatch

router = APIRouter()
domain_regex = r'(https|http)?(://)?(www.)?(?P<domain>(\w|\d|\.)*)\\?.*?'


def generate_thumbnail_path_and_url(fname: str, item_id: int):
    fname = f"{item_id}-{fname}"
    return f"{settings.UPLOADS_FOLDER}/{fname}", f'/static/user_uploads/{fname}'


def extract_filename(r):
    fname = ''
    if "Content-Disposition" in r.headers.keys():
        fname = re.findall("filename=(.+)", r.headers["Content-Disposition"])[0]
    else:
        url = r.request.url
        fname = url.split("/")[-1]

    return (fname)


async def download_thumbnail(src: str, item_id: int):
    for i in range(settings.DOWNLOAD_RETRIES):
        try:
            r = requests.get(src, timeout=settings.DOWNLOAD_TIMEOUT)
            fname = extract_filename(r)
            path, url = generate_thumbnail_path_and_url(fname, item_id)
            with open(path, 'wb') as f:
                f.write(r.content)
            break
        except Exception:
            url = 'ERROR'

    item = await Item.get(pk=item_id)
    item.thumbnail = url
    await item.save(update_fields=["thumbnail", ])


@router.get("/linked/{item_id}", response_model=List[ItemOut], status_code=200)
async def linked_items_top_down(item_id: int):
    """
    Enpoint to showcase top down traversal of linked list starting from any given element
    :param item_id:
    :return:
    """
    db_list = DoublyLinkedList(item_id)
    await db_list.fetch()
    return db_list.items


@router.get("/", response_model=List[ItemOutWithTagsSerialized], status_code=200)
async def read_items(is_favorite: bool = None, tags: List[str] = Query(None)):
    """
    Retrieve all items.
    """
    query_set = Item.all().prefetch_related("tags")
    if is_favorite is not None:
        query_set = query_set.filter(is_favorite=is_favorite)

    if tags:
        query_set = query_set.filter(tags__name__in=tags)

    values = [i.dict() for i in await ItemOut.from_queryset(query_set)]
    return await serialize_tags(values)


async def serialize_tags(values):
    for val in values:
        tags = []
        for t in val['tags']:
            tags.append(t['name'])
        val['tags'] = tags
    return values


@router.get("/{itemd_id}", response_model=ItemOutWithTagsSerialized, status_code=200)
async def read_item(item_id: int,):
    """
    Retrieve item bu id.
    """
    item_dict = ItemOut.from_orm(await Item.get(pk=item_id).prefetch_related("tags")).dict()
    tags = []
    for t in item_dict['tags']:
        tags.append(t['name'])
    item_dict['tags'] = tags
    return item_dict


@router.post("/", status_code=201)
async def create_item(item: ItemCreate,
                      background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Create new item
    """
    async with in_transaction():

        # Create missing tags
        item_tags = item.tags
        if item_tags:
            db_tags = [t['name'] for t in await Tag.all().values("name")]
            non_existent_tags = [Tag(name=tag) for tag in item_tags if tag not in db_tags]
            if non_existent_tags: await Tag.bulk_create(non_existent_tags)

        # Remove key for proper model data validation
        item_dict = item.dict()
        del item_dict['tags']

        # Create item
        db_list = DoublyLinkedList()
        await db_list.init()

        item = await Item.create(**item_dict)
        await db_list.add(item)

        await item.fetch_related("tags")
        if item_tags:
            await item.tags.add(*(await Tag.filter(name__in=item_tags)))

        # Download thumbnails for item
        if item.thumbnail:
            background_tasks.add_task(download_thumbnail, item.thumbnail, item.id)
        else:
            match = re.match(domain_regex, item.url)
            if not match:
                raise Exception("Cannot parse product URL")
            background_tasks.add_task(download_thumbnail, f"https://{match.group('domain')}/favicon.ico", item.id)
        return item


@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int):
    """
    Delete item
    """

    async with in_transaction():
        item = await Item.get(pk=item_id).prefetch_related("next", "previous")
        db_list = DoublyLinkedList()
        await db_list.remove_item(item)
        await item.delete()


@router.patch("/{item_id}", status_code=204)
async def patch_item(item_id: int, item_patch: ItemPatch):
    """
    Patch item
    """
    async with in_transaction():
        item = await Item.get(pk=item_id).prefetch_related("next", "previous")

        if item_patch.previous_id or item_patch.next_id:
            db_list = DoublyLinkedList()
            await db_list.init()
            await db_list.remove_item(item)
            item.previous_id = None
            item.next_id = None
            await db_list.init()

        await item.update_from_dict(item_patch.dict(exclude_unset=True))
        await item.save()

        if item_patch.previous_id or item_patch.next_id:
            await db_list.add(item)
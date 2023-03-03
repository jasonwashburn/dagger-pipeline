"""Main module."""
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

fake_secret_token = "coneofsilence"  # noqa: S105 pylint: disable=invalid-name


app = FastAPI()


class Item(BaseModel):
    """Item model."""

    id: str  # noqa: A003
    title: str
    description: str | None = None


fake_db: dict[str, Item] = {
    "foo": Item(id="foo", title="Foo", description="There goes my hero"),
    "bar": Item(id="bar", title="Bar", description="The bartenders"),
}


@app.get("/items/{item_id}", response_model=Item)
async def read_main(item_id: str, x_token: str = Header()) -> Item:
    """Implement the GET /items/{item_id} endpoint.

    Args:
        item_id (str): An item id.
        x_token (str, optional): X-Token header.

    Raises:
        HTTPException: Status code 400. Invalid X-Token header.
        HTTPException: Status code 404. Item not found.

    Returns:
        dict[str, str]: Item.
    """
    if x_token != fake_secret_token:
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_db[item_id]


@app.post("/items/", response_model=Item)
async def create_item(item: Item, x_token: str = Header()) -> Item:
    """Implement the POST /items/ endpoint.

    Args:
        item (Item): An item.
        x_token (str, optional): X-Token header.

    Raises:
        HTTPException: Status code 400. Invalid X-Token header.
        HTTPException: Status code 400. Item already exists.

    Returns:
        Item: _description_
    """
    if x_token != fake_secret_token:
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    if item.id in fake_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    fake_db[item.id] = item
    return item

"""DynamoDB-backed registry for index metadata."""

from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache

import boto3
from botocore.config import Config as BotoConfig

from app.core.config import get_settings


@dataclass
class IndexInfo:
    """Metadata for a registered index."""

    name: str
    dimension: int
    created_at: str


@lru_cache
def _get_table():
    """Return the DynamoDB Table resource (cached)."""
    settings = get_settings()

    kwargs = {
        "region_name": settings.aws_region,
    }
    if settings.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

    dynamodb = boto3.resource(
        "dynamodb",
        config=BotoConfig(retries={"max_attempts": 3, "mode": "standard"}),
        **kwargs,
    )
    table = dynamodb.Table(settings.dynamodb_table_name)
    return table


def _ensure_table_exists() -> None:
    """Create the DynamoDB table if it does not exist (useful for local dev with LocalStack)."""
    settings = get_settings()

    kwargs = {
        "region_name": settings.aws_region,
    }
    if settings.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

    client = boto3.client("dynamodb", **kwargs)

    existing_tables = client.list_tables()["TableNames"]
    if settings.dynamodb_table_name in existing_tables:
        return

    client.create_table(
        TableName=settings.dynamodb_table_name,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    client.get_waiter("table_exists").wait(TableName=settings.dynamodb_table_name)


def create_index(name: str, dimension: int) -> IndexInfo:
    """Register a new index.

    Args:
        name: Unique index name.
        dimension: Vector dimension for this index.

    Returns:
        IndexInfo for the created index.

    Raises:
        ValueError: If an index with the same name already exists.
    """
    table = _get_table()

    created_at = datetime.now(timezone.utc).isoformat()

    try:
        table.put_item(
            Item={
                "pk": f"INDEX#{name}",
                "name": name,
                "dimension": dimension,
                "created_at": created_at,
            },
            ConditionExpression="attribute_not_exists(pk)",
        )
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        raise ValueError(f"Index '{name}' already exists.")

    return IndexInfo(name=name, dimension=dimension, created_at=created_at)


def get_index(name: str) -> IndexInfo | None:
    """Get index metadata by name.

    Args:
        name: Index name to look up.

    Returns:
        IndexInfo if found, None otherwise.
    """
    table = _get_table()
    response = table.get_item(Key={"pk": f"INDEX#{name}"})
    item = response.get("Item")
    if item is None:
        return None
    return IndexInfo(
        name=item["name"],
        dimension=int(item["dimension"]),
        created_at=item["created_at"],
    )


def list_indexes() -> list[IndexInfo]:
    """List all registered indexes.

    Returns:
        List of IndexInfo for every index in the registry.
    """
    table = _get_table()
    response = table.scan(
        FilterExpression="begins_with(pk, :prefix)",
        ExpressionAttributeValues={":prefix": "INDEX#"},
    )
    items = response.get("Items", [])

    # Handle pagination
    while "LastEvaluatedKey" in response:
        response = table.scan(
            FilterExpression="begins_with(pk, :prefix)",
            ExpressionAttributeValues={":prefix": "INDEX#"},
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        items.extend(response.get("Items", []))

    return [
        IndexInfo(
            name=item["name"],
            dimension=int(item["dimension"]),
            created_at=item["created_at"],
        )
        for item in items
    ]


def delete_index(name: str) -> bool:
    """Remove index from registry.

    Args:
        name: Index name to remove.

    Returns:
        True if the index existed and was removed, False if it was not found.
    """
    table = _get_table()
    try:
        table.delete_item(
            Key={"pk": f"INDEX#{name}"},
            ConditionExpression="attribute_exists(pk)",
        )
        return True
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return False

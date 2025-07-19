Dynamic Fetchers are pluggable components in Eunomia that retrieve entity attributes at runtime. They enable the authorization server to gather metadata about principals and resources from various sources when making policy decisions.

Dynamic Fetchers implement the `fetch_attributes(uri: str)` method to retrieve attributes for entities identified by their URI. Unlike static attributes that are pre-configured, dynamic fetchers allow Eunomia to pull fresh metadata from external systems, databases, or APIs during the authorization process.

This dynamic approach enables:

- **Real-time attribute retrieval**: Get the latest entity metadata when evaluating policies
- **External system integration**: Connect to databases, APIs, or other services for attribute data
- **Flexible architecture**: Plug in custom fetchers for any use case

## Configuration

Dynamic Fetchers can be configured through the `FETCHERS` variable in your Eunomia settings, which can be passed as an environment variable:

```
FETCHERS = {"registry": {...}, "passport": {...}}
```

## Built-in Fetchers

Eunomia comes with some built-in fetchers:

| Fetcher    | Description                                              | Jump to                                          |
| ---------- | -------------------------------------------------------- | ------------------------------------------------ |
| `registry` | Stores and retrieves entity attributes in a SQL database | [:material-arrow-right: Page](registry/index.md) |

## Creating a Custom Fetcher

To create a custom fetcher, you need to subclass the `BaseFetcher` class and implement the `fetch_attributes(uri: str)` method.

```python
from eunomia.fetchers.base import BaseFetcher, BaseFetcherConfig


class CustomFetcherConfig(BaseFetcherConfig):
    pass


class CustomFetcher(BaseFetcher):
    config: CustomFetcherConfig

    async def fetch_attributes(self, uri: str) -> dict:
        # your custom logic here
        return {}
```

Then, you can register the fetcher within the `FetcherFactory` to make it available for use:

```python
from eunomia.fetchers.factory import FetcherFactory

FetcherFactory.register_fetcher(
    "custom",
    CustomFetcher,
    CustomFetcherConfig,
)
```

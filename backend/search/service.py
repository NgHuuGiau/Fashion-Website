"""Meilisearch Search Service"""

import logging
from dataclasses import dataclass
from typing import Any, Optional

import meilisearch
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class SearchConfig:
    host: str = "http://localhost:7700"
    api_key: str = ""
    index_name: str = "products"
    timeout: int = 5

    @classmethod
    def from_settings(cls) -> "SearchConfig":
        return cls(
            host=getattr(settings, "MEILISEARCH_HOST", "http://localhost:7700"),
            api_key=getattr(settings, "MEILISEARCH_API_KEY", ""),
            index_name=getattr(settings, "MEILISEARCH_INDEX_NAME", "products"),
        )

    def is_configured(self) -> bool:
        return bool(self.host)


class SearchService:
    """Meilisearch integration for product search with filters, facets, autocomplete"""

    def __init__(self, config: SearchConfig = None):
        self.config = config or SearchConfig.from_settings()
        self.client = None
        self.index = None
        if self.config.is_configured():
            self.client = meilisearch.Client(self.config.host, self.config.api_key)
            self.index = self.client.index(self.config.index_name)

    def is_available(self) -> bool:
        return self.client is not None

    def setup_index(self) -> bool:
        if not self.is_available():
            return False
        try:
            self.client.create_index(self.config.index_name, {"primaryKey": "id"})
            index = self.client.index(self.config.index_name)
            index.update_searchable_attributes(["name", "description", "category_name", "brand_name", "sku", "tags"])
            index.update_filterable_attributes(["category_id", "brand_id", "category_slug", "brand_slug", "price", "is_active", "is_featured", "colors", "sizes", "tags"])
            index.update_sortable_attributes(["price", "created_at", "updated_at", "popularity"])
            index.update_facet_attributes(["category_name", "brand_name", "colors", "sizes", "price_range"])
            index.update_typo_tolerance({"enabled": True, "minWordSizeForTypos": {"oneTypo": 4, "twoTypos": 8}})
            index.update_synonyms({"ao thun": ["t-shirt", "tee", "a thun"], "quan jean": ["denim", "jean", "quan bau"], "vay": ["dress", "vay dep"], "giay": ["sneaker", "boot", "sandal"], "tui": ["bag", "handbag", "backpack"], "phu kien": ["accessory", "accessories"]})
            index.update_stop_words(["va", "cua", "cho", "voi", "tai", "trong", "ngoai", "tren", "duoi", "giua", "canh", "gan", "xa"])
            logger.info("Meilisearch index configured successfully")
            return True
        except Exception as e:
            logger.error("Failed to setup Meilisearch index: %s", e)
            return False

    def index_product(self, product) -> bool:
        if not self.is_available():
            return False
        try:
            doc = self._product_to_document(product)
            self.index.add_documents([doc])
            return True
        except Exception as e:
            logger.error("Failed to index product %s: %s", product.id, e)
            return False

    def index_products_batch(self, products) -> bool:
        if not self.is_available():
            return False
        try:
            docs = [self._product_to_document(p) for p in products]
            self.index.add_documents(docs)
            return True
        except Exception as e:
            logger.error("Failed to batch index products: %s", e)
            return False

    def delete_product(self, product_id: int) -> bool:
        if not self.is_available():
            return False
        try:
            self.index.delete_document(str(product_id))
            return True
        except Exception as e:
            logger.error("Failed to delete product %s: %s", product_id, e)
            return False

    def search(self, query: str = "", filters: dict = None, facets: list = None, sort: list = None, page: int = 1, hits_per_page: int = 20, attributes_to_retrieve: list = None) -> dict:
        if not self.is_available():
            return {"hits": [], "total_hits": 0, "page": 1, "total_pages": 0}
        try:
            search_params = {
                "q": query,
                "page": page,
                "hitsPerPage": hits_per_page,
                "attributesToRetrieve": attributes_to_retrieve or ["id", "name", "slug", "price", "compare_price", "image", "image_url", "category_name", "brand_name", "colors", "sizes", "is_featured", "discount_percent"],
                "attributesToHighlight": ["name", "description"],
                "highlightPreTag": "<mark>",
                "highlightPostTag": "</mark>",
            }
            if filters:
                filter_parts = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        val_str = ", ".join(map(str, value))
                        filter_parts.append(key + " IN [" + val_str + "]")
                    elif isinstance(value, (int, float)):
                        filter_parts.append(key + " = " + str(value))
                    else:
                        filter_parts.append(key + " = '" + str(value) + "'")
                search_params["filter"] = " AND ".join(filter_parts)
            if facets:
                search_params["facets"] = facets
            if sort:
                search_params["sort"] = sort
            result = self.index.search(query, search_params)
            return {
                "hits": result.get("hits", []),
                "total_hits": result.get("estimatedTotalHits", 0),
                "page": result.get("page", 1),
                "total_pages": result.get("totalPages", 0),
                "processing_time_ms": result.get("processingTimeMs", 0),
                "facets_distribution": result.get("facetDistribution", {}),
                "query": query,
            }
        except Exception as e:
            logger.error("Search failed: %s", e)
            return {"hits": [], "total_hits": 0, "page": 1, "total_pages": 0}

    def autocomplete(self, query: str, limit: int = 10) -> list:
        if not self.is_available():
            return []
        try:
            result = self.index.search(query, {"hitsPerPage": limit, "attributesToRetrieve": ["id", "name", "slug", "image", "price"], "attributesToHighlight": ["name"], "highlightPreTag": "<mark>", "highlightPostTag": "</mark>"})
            return result.get("hits", [])
        except Exception as e:
            logger.error("Autocomplete failed: %s", e)
            return []

    def get_facet_values(self, facet_name: str, filters: dict = None) -> dict:
        if not self.is_available():
            return {}
        try:
            search_params = {"q": "", "hitsPerPage": 0, "facets": [facet_name]}
            if filters:
                filter_parts = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        val_str = ", ".join(map(str, value))
                        filter_parts.append(key + " IN [" + val_str + "]")
                    else:
                        filter_parts.append(key + " = '" + str(value) + "'")
                search_params["filter"] = " AND ".join(filter_parts)
            result = self.index.search("", search_params)
            return result.get("facetDistribution", {}).get(facet_name, {})
        except Exception as e:
            logger.error("Get facet values failed: %s", e)
            return {}

    def _product_to_document(self, product) -> dict:
        from products.models import ProductVariant
        variants = product.variants.filter(is_active=True).select_related()
        colors = []
        sizes = []
        min_price = product.price
        max_price = product.price
        skus = []
        for variant in variants:
            if variant.color_name and variant.color_name not in colors:
                colors.append(variant.color_name)
            if variant.size and variant.size not in sizes:
                sizes.append(variant.size)
            if variant.price < min_price:
                min_price = variant.price
            if variant.price > max_price:
                max_price = variant.price
            if hasattr(variant, "sku") and variant.sku:
                skus.append(variant.sku)
        price_ranges = []
        if min_price < 200000:
            price_ranges.append("under_200k")
        elif min_price < 500000:
            price_ranges.append("200k_500k")
        elif min_price < 1000000:
            price_ranges.append("500k_1m")
        else:
            price_ranges.append("over_1m")
        return {
            "id": str(product.id),
            "name": product.name,
            "slug": product.slug,
            "description": product.description or "",
            "price": float(product.price),
            "compare_price": float(product.compare_price) if product.compare_price else None,
            "min_price": float(min_price),
            "max_price": float(max_price),
            "discount_percent": product.discount_percent,
            "image": product.get_image() if hasattr(product, "get_image") else "",
            "image_url": product.image_url or "",
            "category_id": product.category_id,
            "category_name": product.category.name if product.category else "",
            "category_slug": product.category.slug if product.category else "",
            "brand_id": getattr(product, "brand_id", None),
            "brand_name": getattr(product, "brand", None).name if getattr(product, "brand", None) else "",
            "brand_slug": getattr(product, "brand", None).slug if getattr(product, "brand", None) else "",
            "is_active": product.available,
            "is_featured": product.featured,
            "stock": product.get_total_stock() if hasattr(product, "get_total_stock") else product.stock,
            "colors": colors,
            "sizes": sizes,
            "skus": skus,
            "price_ranges": price_ranges,
            "tags": getattr(product, "tags", []),
            "created_at": product.created.timestamp() if product.created else 0,
            "updated_at": product.updated.timestamp() if product.updated else 0,
            "popularity": getattr(product, "view_count", 0) + getattr(product, "order_count", 0) * 10,
        }


# Singleton instance
_search_service = None

def get_search_service() -> Optional[SearchService]:
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service

def reindex_all_products() -> bool:
    from products.models import Product
    service = get_search_service()
    if not service or not service.is_available():
        return False
    service.setup_index()
    products = Product.objects.filter(available=True).select_related("category", "brand").prefetch_related("variants")
    batch_size = 100
    for i in range(0, products.count(), batch_size):
        batch = list(products[i:i + batch_size])
        if not service.index_products_batch(batch):
            logger.error("Failed to index batch starting at %s", i)
            return False
    logger.info("Reindexed %s products", products.count())
    return True

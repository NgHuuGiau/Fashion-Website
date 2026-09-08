"""Management command to generate OpenAPI schema from Django URL patterns."""

import json
import yaml
from django.core.management.base import BaseCommand
from django.urls import get_resolver


class Command(BaseCommand):
    help = "Generate OpenAPI schema from Django URL patterns"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="openapi.yaml",
            help="Output file path (default: openapi.yaml)",
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=["yaml", "json"],
            default="yaml",
            help="Output format (default: yaml)",
        )

    def handle(self, *args, **options):
        output_file = options["output"]
        format_type = options["format"]

        # Get all URL patterns
        resolver = get_resolver()
        paths = self._extract_paths(resolver)

        # Build OpenAPI spec
        schema = {
            "openapi": "3.0.3",
            "info": {
                "title": "HUUGIAU Fashion API",
                "version": "1.0.0",
                "description": "API documentation for HUUGIAU Fashion E-commerce",
                "contact": {"name": "HUUGIAU Studio", "email": "support@huugiau.local"},
                "license": {"name": "MIT"},
            },
            "servers": [{"url": "/api/", "description": "API base URL"}],
            "paths": paths,
            "components": {
                "schemas": self._get_common_schemas(),
            },
            "tags": [
                {"name": "Products", "description": "Product catalog and details"},
                {"name": "Orders", "description": "Order management and checkout"},
                {"name": "Users", "description": "Authentication and user profile"},
                {"name": "Admin", "description": "Admin-only endpoints"},
            ],
        }

        # Write output
        if format_type == "json":
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(schema, f, ensure_ascii=False, indent=2)
        else:
            with open(output_file, "w", encoding="utf-8") as f:
                yaml.dump(schema, f, allow_unicode=True, sort_keys=False)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated OpenAPI schema to {output_file}"
            )
        )

    def _extract_paths(self, resolver):
        """Extract paths from URL resolver."""
        paths = {}

        def extract_patterns(patterns, prefix=""):
            for pattern in patterns:
                if hasattr(pattern, "url_patterns"):
                    # Include pattern
                    extract_patterns(
                        pattern.url_patterns, prefix + str(pattern.pattern)
                    )
                else:
                    # URL pattern
                    path = prefix + str(pattern.pattern)
                    path = path.replace("^", "").replace("$", "")
                    path = "/" + path.lstrip("/")

                    # Get view info
                    view = pattern.callback
                    view_name = getattr(view, "__name__", "unknown")

                    # Determine HTTP methods
                    methods = getattr(view, "http_method_names", ["get"])

                    # Build path entry
                    path_entry = {}
                    for method in methods:
                        if method.lower() in [
                            "get",
                            "post",
                            "put",
                            "patch",
                            "delete",
                            "head",
                            "options",
                        ]:
                            path_entry[method.lower()] = self._build_operation(
                                view, view_name, method.lower()
                            )

                    if path_entry:
                        paths[path] = path_entry

        extract_patterns(resolver.url_patterns)
        return paths

    def _build_operation(self, view, view_name, method):
        """Build OpenAPI operation from view."""
        docstring = getattr(view, "__doc__", "") or ""
        summary = docstring.strip().split("\n")[0] if docstring else view_name

        operation = {
            "summary": summary[:100],
            "description": docstring.strip() if docstring else "",
            "responses": {
                "200": {"description": "Successful response"},
                "400": {"description": "Bad request"},
                "401": {"description": "Unauthorized"},
                "403": {"description": "Forbidden"},
                "404": {"description": "Not found"},
                "500": {"description": "Internal server error"},
            },
            "tags": self._get_tags(view),
        }

        # Add request body for POST/PUT/PATCH
        if view_name in [
            "api_review_submit",
            "api_coupon_check",
            "api_admin_order_status",
            "api_admin_order_refund",
        ]:
            operation["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"type": "object"}}},
            }

        # Add parameters for paths with pk
        if "{pk}" in view.__name__ or "pk" in str(view):
            # This is simplified - in reality we'd inspect URL pattern
            pass

        return operation

    def _get_tags(self, view):
        """Determine tags for a view."""
        module = getattr(view, "__module__", "")

        if "product" in module or "product" in view.__name__:
            return ["Products"]
        elif "order" in module or "order" in view.__name__:
            return ["Orders"]
        elif "user" in module or "auth" in module:
            return ["Users"]
        elif "admin" in module or "admin" in view.__name__:
            return ["Admin"]
        return ["API"]

    def _get_common_schemas(self):
        """Define common reusable schemas."""
        return {
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                },
            },
            "Product": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "slug": {"type": "string"},
                    "price": {"type": "integer"},
                    "image_url": {"type": "string"},
                    "category": {"type": "string"},
                    "rating_avg": {"type": "number", "format": "float"},
                    "review_count": {"type": "integer"},
                },
            },
            "Order": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "status": {"type": "string"},
                    "total_amount": {"type": "integer"},
                    "created_at": {"type": "string", "format": "date-time"},
                },
            },
        }

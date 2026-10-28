from ..http_client import http_client


class CatalogMcps:

    @staticmethod
    def register_mcp(mcp):

        @mcp.tool()
        def get_all_categories():
            """
            Get all top-level Fixji service categories.

            Use when a customer asks what kinds of services Fixji provides,
            or when category names are needed to navigate the catalog.

            Returns categories and the subcategory/count information supplied
            by the backend. This is not guaranteed to contain every service.
            Backend API: GET /api/catalog/categories
            """
            return http_client.api_get("api/catalog/categories")

        @mcp.tool()
        def get_services(category_id: str = "", subcategory_id: str = ""):
            """
            Get Fixji's service catalog, optionally filtered by category
            or subcategory UUID.

            Use when the customer asks to see all services, or requests a
            catalog listing within a known category or subcategory.

            IDs must come from actual Fixji API results; never invent them.
            Backend API: GET /api/catalog/services
            Optional query parameters: category_id, subcategory_id
            """
            params = {"category_id": category_id, "subcategory_id": subcategory_id}
            return http_client.api_get("api/catalog/services", params=params)

        @mcp.tool()
        def get_service_details(service_id: str, pincode: str = ""):
            """
            Get a specific service's details and related professionals.

            Use after the catalog identifies a relevant service and its UUID.
            The optional PIN code requests location-specific partner results
            where supported by the backend.

            Never guess or generate service UUIDs.
            Backend API: GET /api/catalog/services/{id}?pincode=...
            """
            if not service_id or not service_id.strip():
                return {"success": False, "error": "A non-empty service_id is required."}

            if pincode and not (pincode.isdigit() and len(pincode) == 6):
                return {"success": False, "error": "PIN code must contain exactly 6 digits."}

            return http_client.api_get(
                f"api/catalog/services/{service_id.strip()}",
                params={"pincode": pincode},
            )
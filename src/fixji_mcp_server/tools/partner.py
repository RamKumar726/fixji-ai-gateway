from ..http_client import http_client
from datetime import date

class PartnerMCP:
    def register_mcp(mcp):
        @mcp.tool()
        def find_partners(
            service_id: str = "",
            category_id: str = "",
            subcategory_id: str = "",
            pincode: str = "",
        ):
            """
            Find Fixji professionals using supported catalog and location filters.

            Prefer service_id when a matching service has already been selected.
            Use category_id or subcategory_id when discovering professionals
            across a broader service area.

            The backend returns partner data such as ratings, experience,
            service counts and PIN codes served, where available.

            Backend API: GET /api/partners/
            Supported query parameters: service_id, category_id,
            subcategory_id, pincode
            """
            if pincode and not (pincode.isdigit() and len(pincode) == 6):
                return {"success": False, "error": "PIN code must contain exactly 6 digits."}

            return http_client.api_get(
                "api/partners/",
                {
                    "service_id": service_id.strip(),
                    "category_id": category_id.strip(),
                    "subcategory_id": subcategory_id.strip(),
                    "pincode": pincode,
                },
            )

        @mcp.tool()
        def get_partner_slots(partner_id: str, booking_date: str):
            """
            Check actual appointment slots for a Fixji professional on a date.

            Use after the customer has selected a matching professional and
            wants to know which appointment windows are available.

            partner_id must be the exact partner UUID returned by Fixji.
            booking_date must use YYYY-MM-DD.

            Backend API:
            GET /api/partners/{id}/slots?date=YYYY-MM-DD
            """
            if not partner_id or not partner_id.strip():
                return {"success": False, "error": "Partner ID is required."}

            try:
                parsed = date.fromisoformat(booking_date)
                if parsed.isoformat() != booking_date:
                    raise ValueError
            except ValueError:
                return {"success": False, "error": "Use YYYY-MM-DD for the booking date."}

            if parsed < date.today():
                return {"success": False, "error": "The booking date cannot be in the past."}

            return http_client.api_get(
                f"api/partners/{partner_id.strip()}/slots",
                {"date": booking_date},
            )
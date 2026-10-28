from ..http_client import  http_client
from ..config import settings
from fastmcp.server.dependencies import get_http_headers


class BookingMCP:
    def register_mcp(mcp):

        @mcp.tool()
        def create_booking(
        service_id: str,
        partner_id: str,
        booking_date: str,
        time_slot: str,
        service_address: str,
        customer_pincode: str,
        customer_notes: str = "",
        coupon_code: str = "",
        payment_mode: str = "PAY_AFTER_SERVICE",
        ):
            """
            Create a Fixji home-service booking after explicit customer
            confirmation of the service, professional, date, slot, address,
            PIN code, and payment mode.

            All IDs must come from actual Fixji API responses.
            The customer's auth token is injected by the trusted application;
            never ask the customer to paste it into chat.

            Backend API:
            POST /api/bookings
            Requires Authorization: Bearer <customer JWT>.
            """
            auth_header = get_http_headers(include_all=True).get("authorization")
            if not auth_header:
                return {"success": False, "error": "Customer is not logged in."}

            required = {
                "service_id": service_id,
                "partner_id": partner_id,
                "booking_date": booking_date,
                "time_slot": time_slot,
                "service_address": service_address,
                "customer_pincode": customer_pincode,
            }
            missing = [k for k, v in required.items() if not v or not v.strip()]
            if missing:
                return {
                    "success": False,
                    "error": "Missing required fields.",
                    "missing_fields": missing,
                }

            payload = {
                "service_id": service_id,
                "partner_id": partner_id,
                "booking_date": booking_date,
                "time_slot": time_slot,
                "service_address": service_address,
                "customer_pincode": customer_pincode,
                "customer_notes": customer_notes,
                "payment_mode": payment_mode,
            }
            # Note: coupon_code was never sent in your original code either.
            # Kept the same; we can wire it in later once your backend supports it.

            return http_client.api_post(
                "api/bookings",
                payload,
                headers={"Authorization": auth_header},
                timeout=settings.BOOKING_TIMEOUT,
            )
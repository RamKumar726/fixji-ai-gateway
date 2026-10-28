from .catalog import CatalogMcps
from .partner import PartnerMCP
from .booking import BookingMCP

def register_all_mcps(mcp):
    CatalogMcps.register_mcp(mcp)
    PartnerMCP.register_mcp(mcp)
    BookingMCP.register_mcp(mcp)
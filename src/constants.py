"""
 "  Configuration
"""
# EDDN
EDDN_URI = "tcp://eddn.edcd.io:9500"
EDDN_TIMEOUT = 600000

# Bubble Limits
BUBBLE_LIMIT_LOW = -500
BUBBLE_LIMIT_HIGH = 500

# Database
DATABASE_HOST = "10.0.0.52"
DATABASE_URI = f"mongodb://{DATABASE_HOST}:27017"

# Filtering
IGNORE_THESE = [
    "System Colonisation Ship",
    "Stronghold Carrier",
    "OnFootSettlement",
    "Colonisation",
    "$EXT_PANEL_ColonisationShip; [inactive]",
]

def get_week_of_cycle():
    with open("week.txt", "r") as f:
        data = f.read().strip()
        f.close()
    return int(data)
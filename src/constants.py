import sqlalchemy
from sqlalchemy import BigInteger, String, Column, Boolean, Integer, Float, BOOLEAN

Base = sqlalchemy.orm.declarative_base()


"""
 "  Configuration
"""
# EDDN
EDDN_URI = "tcp://eddn.edcd.io:9500"
"""EDDN TCP URI"""
EDDN_TIMEOUT = 600000
"""How long to wait before reconnecting"""
VALID_CLIENT_VERSION = ["4", "1", "2", "100"]
""" Minimum client version to not be ignored """
MESSAGE_TIMEOUT = 5
"""How many minutes until a message is considered old?"""

# Bubble Limits
BUBBLE_LIMIT_LOW = -600
BUBBLE_LIMIT_HIGH = 600

# Database
DATABASE_HOST = "10.0.0.52"
DATABASE_URI = f"mysql+pymysql://assistant:6548@{DATABASE_HOST}/elite"

# Filtering
IGNORE_THESE = [
    "System Colonisation Ship",
    "Stronghold Carrier",
    "OnFootSettlement",
    "Colonisation",
    "$EXT_PANEL_ColonisationShip; [inactive]",
    "'$EXT_PANEL_ColonisationShip:#index=",
    "Carrier",
    "EXT_PANEL",
    "Construction Site",
    "$EXT_PANEL_ColonisationShip:#index=",
    "$EXT_PANEL_ColonisationShip:#index=1;",
    "$EXT_PANEL_ColonisationShip:#index=2;",
    "$EXT_PANEL_ColonisationShip:#index=3;",
    "GameGlass"
]
"""If a name contains one of these, ignore it"""

def power_full_to_short(power: str) -> str:
    """
    Returns the shortcode of a power when supplied its full name
    """
    for key, value in POWERS.items():
        if value == power:
            return key
    return ""

def short_to_full_power(power: str) -> str:
    """
    Retuns the full name of a power when supplied its shortcode
    """
    if power == '':
        return ""
    return POWERS[power]

def should_be_ignored(item: str) -> bool:
    for ingore in IGNORE_THESE:
        if ingore in item:
            return True
    return False


def get_week_of_cycle():
    with open("week.txt", "r") as f:
        data = f.read().strip()
        f.close()
    return int(data)

POWERS = {
    "ALD": 'A. Lavigny-Duval',
    "ARD": 'Archon Delaine',
    "ASD": "Aisling Duval",
    "DPT": 'Denton Patreus',
    "EMH": "Edmund Mahon",
    "FLW": "Felicia Winters",
    "JRA": "Jerome Archer",
    "LYR": "Li Yong-Rui",
    "NAK": "Nakato Kaine",
    "PRA": 'Pranav Antal',
    "YRG": "Yuri Grom",
    "ZMT": "Zemina Torval",
}
"""
The powers and their shortcodes
"""


class StarSystem(Base):
    __tablename__ = "star_systems"
    system_name = Column(String(255), primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    height = Column(Float)
    is_anarchy = Column(Boolean)


# class Station(Base):
#     """
#     Represents a entry in the stations table
#     """

#     __tablename__ = "stations"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     station_name = Column(String(255))
#     star_system = Column(String(255))
#     station_type = Column(String(255))
#     economy = Column(String(255))


class Megaship(Base):
    __tablename__ = "megaships"
    name = Column(String(255), primary_key=True)
    SYSTEM1 = Column(String(255))
    SYSTEM2 = Column(String(255))
    SYSTEM3 = Column(String(255))
    SYSTEM4 = Column(String(255))
    SYSTEM5 = Column(String(255))
    SYSTEM6 = Column(String(255))


class PowerData(Base):
    __tablename__ = "powerdata"
    system_name = Column(String(50), primary_key=True)
    state = Column(String(20))
    """Unoccupied, War, Exploited, Fortified or Stronghold"""
    shortcode = Column(String(4))
    control_points = Column(Float())
    points_change = Column(Float())
    
class Conflicts(Base):
    __tablename__ = "conflicts"
    system_name = Column(String(50), primary_key=True)
    first_place = Column(String(4))
    second_place = Column(String(4))
    has_czs = Column(BOOLEAN(False))
    cycle = Column(Integer())
import sqlalchemy
from sqlalchemy import String, Column, Boolean, Integer, Float, BOOLEAN

Base = sqlalchemy.orm.declarative_base()


"""
 "  Configuration
"""
# EDDN
EDDN_URI = "tcp://eddn.edcd.io:9500"
EDDN_TIMEOUT = 600000
VALID_CLIENT_VERSION = ["4", "1", "1", "0"]
MESSAGE_TIMEOUT = 5
"""How many minutes until a message is considered old?"""

# Bubble Limits
BUBBLE_LIMIT_LOW = -500
BUBBLE_LIMIT_HIGH = 500

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
]


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
    "ALD": "Arissa Lavingy-Duval",
    "ARD": "Archon Delane",
    "ASD": "Aisling Duval",
    "DPT": "Denton Patrus",
    "EMH": "Edmund Mahon",
    "FLW": "Felicia Winters",
    "JRA": "Jerome Archer",
    "LYR": "Li Yong-Rui",
    "NAK": "Nakato Kaine",
    "PRA": "Prantav Antal",
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


class Station(Base):
    """
    Represents a entry in the stations table
    """

    __tablename__ = "stations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    station_name = Column(String(255))
    star_system = Column(String(255))
    station_type = Column(String(255))
    economy = Column(String(255))


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
    shortcode = Column(String(4))
    war = Column(BOOLEAN(False))
    war_start = Column(Integer())


class PowerPoints(Base):
    __tablename__ = "powerpoints"
    id = Column(Integer, primary_key=True)
    shortcode = Column(String, nullable=False)
    exploited = Column(Integer, nullable=False)
    fortified = Column(Integer, nullable=False)
    stronghold = Column(Integer, nullable=False)
    cycle = Column(Integer, nullable=False)
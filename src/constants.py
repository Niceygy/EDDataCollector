import sqlalchemy
from sqlalchemy import String, Column, Boolean, Integer, Float 

Base = sqlalchemy.orm.declarative_base()


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
DATABASE_URI = f"mysql+pymysql://assistant:6548@{DATABASE_HOST}/elite"

# Filtering
IGNORE_THESE = [
    "System Colonisation Ship",
    "Stronghold Carrier",
    "OnFootSettlement",
    "Colonisation",
    "$EXT_PANEL_ColonisationShip; [inactive]",
    "'$EXT_PANEL_ColonisationShip:#index=1;'"
]

def get_week_of_cycle():
    with open("week.txt", "r") as f:
        data = f.read().strip()
        f.close()
    return int(data)


class StarSystem(Base):
    __tablename__ = "star_systems"
    system_name = Column(String(255), primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    height = Column(Float)
    #state = Column(String(255))
    #shortcode = Column(String(255))
    is_anarchy = Column(Boolean)


class Station(Base):
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
    controlPointsStart = Column(Float())
    controlPointsLatest = Column(Float())
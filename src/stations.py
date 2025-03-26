from sqlalchemy import and_
from constants import IGNORE_THESE, Station
from sqlalchemy.orm import sessionmaker as sm


def add_station(
    session: sm, station_name: str, station_type: str, system_name: str, economy: str
):
    """
    Adds a station. Only used when we detect station signals, 
    as these only contain non-updating data 
    (such as the economy, name, ect)

    Args:
        session (sm): Database session object
        station_name (str): Station Name
        station_type (str): Station Type
        system_name (str): System Name
        economy (str): Economy
    """
    system_name = str(system_name).replace("'", ".")
    if station_name in IGNORE_THESE:
        return
    # is already in database?
    station = (
        session.query(Station)
        .filter(
            and_(
                Station.star_system == system_name, Station.station_name == station_name
            )
        )
        .first()
    )

    # station type
    match station_type:
        case "Coriolis":
            station_type = "Starport"
        case "Orbis":
            station_type = "Starport"
        case "Ocellus":
            station_type = "Starport"

    if station is None:
        # not already in db, add it
        new_station = Station(
            star_system=system_name,
            station_name=station_name,
            station_type=station_type,
            economy=economy,
        )
        session.add(new_station)


def alter_station_data(station_name: str, system_name: str, economy: str, station_type: str, session: sm):
    system_name = str(system_name).replace("'", ".")

    if station_name in IGNORE_THESE:
        return
    # is already in database?
    station = (
        session.query(Station)
        .filter(
            and_(
                Station.star_system == system_name, Station.station_name == station_name
            )
        )
        .first()
    )

    # station type
    match station_type:
        case "Coriolis":
            station_type = "Starport"
        case "Orbis":
            station_type = "Starport"
        case "Ocellus":
            station_type = "Starport"

    if station is None:
        # not already in db, add it
        new_station = Station(
            star_system=system_name,
            station_name=station_name,
            station_type=station_type,
            economy=economy,
        )
        session.add(new_station)
        return
    else:
        # print(f"Changed {station_name}'s (in {system_name}) economy to {economy}")
        station.economy = economy
        return

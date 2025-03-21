from sqlalchemy import and_
from constants import IGNORE_THESE, Station
from sqlalchemy.orm import sessionmaker as sm


def add_station(session: sm, station_name: str, station_type: str, system_name: str, economy: str):
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


def alter_station_data(station_name, system_name, economy, station_type, session):
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
        # Update a single record
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

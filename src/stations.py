from constants import IGNORE_THESE

def add_station(database, station_name, station_type, system_name, economy):
    system_name = str(system_name).replace("'", ".")
    if station_name in IGNORE_THESE:
        return
    # is already in database?
    station_collection = database["stations"]
    station = station_collection.find({"system_name": system_name})

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
        station_collection.insert_one(
            {
                "station_name": station_name,
                "system_name": system_name,
                "station_type": station_type,
                "economy": economy,
            }
        )


def alter_station_data(station_name, system_name, economy, station_type, database):
    system_name = str(system_name).replace("'", ".")

    if station_name in IGNORE_THESE:
        return
    # is already in database?
    station_collection = database["stations"]
    station = station_collection.find({"system_name": system_name})

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
        station_collection.insert_one(
            {
                "station_name": station_name,
                "system_name": system_name,
                "station_type": station_type,
                "economy": economy,
            }
        )
        return
    else:
        # print(f"Changed {station_name}'s (in {system_name}) economy to {economy}")
        station_collection.update_one(
            {"system_name": system_name, "station_name": station_name},
            {"$set": {"economy": economy}},
        )
        return

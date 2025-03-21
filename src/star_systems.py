from constants import BUBBLE_LIMIT_HIGH, BUBBLE_LIMIT_LOW


def add_system(
    database,
    system_name,
    latitude,
    longitude,
    height,
    state,
    shortcode,
    is_anarchy,
):

    # Is in bubble?
    if (
        latitude > BUBBLE_LIMIT_HIGH
        or latitude < BUBBLE_LIMIT_LOW
        or longitude > BUBBLE_LIMIT_HIGH
        or longitude < BUBBLE_LIMIT_LOW
        or height > BUBBLE_LIMIT_HIGH
        or height < BUBBLE_LIMIT_LOW
    ):
        return
    else:
        system_name = str(system_name).replace("'", ".")
        # is already in database?
        system_collection = database["star_systems"]
        system = system_collection.find_one({"system_name": system_name})
        
        if state == '':
            state = "Unoccupied"

        if system is None:
            # not already in db, add it
            system_collection.insert_one(
                {
                    'system_name': system_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "height": height,
                    "state": state,
                    "shortcode": shortcode,
                    "is_anarchy": is_anarchy,
                }
            )
        else:
            if system and system.get("height") is None:
                # part filled in, finish the rest
                # Update a single record in the add_system function
                system_collection.update_one(
                    {"system_name": system_name},
                    {"$set": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "height": height,
                        "state": state,
                        "shortcode": shortcode,
                        "is_anarchy": is_anarchy
                    }}
                )
            else:
                # already in db, update
                system_collection.update_one(
                    {"system_name": system_name},
                    {"$set": {
                        "state": state,
                        "shortcode": shortcode,
                        "is_anarchy": is_anarchy
                    }}
                )
from constants import BUBBLE_LIMIT_HIGH, BUBBLE_LIMIT_LOW
# from pymongo import 


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
        system = system_collection.find({"system_name": system_name})

        if system is None or 'system_name' not in system:
            # not already in db, add it
            print("not exists " + system_name)
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
            print("exists!")
            if system.height is None:
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
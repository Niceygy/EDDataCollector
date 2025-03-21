from constants import BUBBLE_LIMIT_HIGH, BUBBLE_LIMIT_LOW, StarSystem


def add_system(
    session,
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
        system = session.query(StarSystem).filter_by(system_name=system_name).first()
        
        if state == '':
            state = "Unoccupied"

        if system is None:
            # not already in db, add it
            new_system = StarSystem(
                system_name=system_name,
                latitude=latitude,
                longitude=longitude,
                height=height,
                state=state,
                shortcode=shortcode,
                is_anarchy=is_anarchy,
            )
            session.add(new_system)
        else:
            if system is None or system.height is None:
                # part filled in, finish the rest
                # Update a single record in the add_system function
                system.height = height
                system.latitude = latitude,
                system.longitude = longitude
                system.shortcode = shortcode
                system.state = state
                system.is_anarchy = is_anarchy
            else:
                # already in db, update
                system.shortcode = shortcode
                system.state = state
                system.is_anarchy = is_anarchy
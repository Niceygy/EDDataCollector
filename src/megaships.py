from constants import get_week_of_cycle, IGNORE_THESE, Megaship
from sqlalchemy.orm import sessionmaker as sm

def add_megaship(megaship_name: str, new_system: str, session: sm):
    try:
        if megaship_name in IGNORE_THESE:
            return

        week = get_week_of_cycle()
        system_mapping = {
            1: "SYSTEM1",
            2: "SYSTEM2",
            3: "SYSTEM3",
            4: "SYSTEM4",
            5: "SYSTEM5",
            6: "SYSTEM6",
        }
        if week not in system_mapping:
            return
    
        megaship = session.query(Megaship).filter_by(name=megaship_name).first()
        if megaship is not None:
            # entry exists
            system_attribute = system_mapping.get(week)
            if system_attribute is not None and getattr(megaship, system_attribute) is None:
                # entry for this week does not exist, update it
                match week:
                    case 1:
                        megaship.SYSTEM1 = new_system
                    case 2:
                        megaship.SYSTEM2 = new_system
                    case 3:
                        megaship.SYSTEM3 = new_system
                    case 4:
                        megaship.SYSTEM4 = new_system
                    case 5:
                        megaship.SYSTEM5 = new_system
                    case 6:
                        megaship.SYSTEM6 = new_system
                session.add(megaship)
        else:
            new_megaship = Megaship()

            if week in system_mapping:
                new_megaship = Megaship(
                    name=megaship_name, **{system_mapping[week]: new_system}
                )
                session.add(new_megaship)
                return
            else:
                raise ValueError("Invalid week number")
    except Exception as e:
        print(e)

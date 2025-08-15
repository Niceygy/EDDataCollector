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
            if system_attribute is not None:
                current_system = getattr(megaship, system_attribute)
                if current_system is None:
                    # entry for this week does not exist, update it
                    setattr(megaship, system_attribute, new_system)
                    session.add(megaship)
                elif current_system != new_system:
                    # print(f"Updating {megaship_name} {system_attribute} from {current_system} to {new_system}")
                    setattr(megaship, system_attribute, new_system)
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

from constants import get_week_of_cycle, IGNORE_THESE

def add_megaship(megaship_name, new_system, database):
    megaship_collection = database["megaships"]

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
    
    megaship = megaship_collection.find({'name': megaship_name})
    if megaship is not None:
        if system_mapping[week] in megaship:
            #entry set up correctly
            stored_system = megaship[system_mapping[week]]
            if stored_system != new_system:
                #don't match! update it :)
                megaship_collection.update_one(
                    {"name": megaship_name},
                    {"$set": {
                        f'{system_mapping[week]}': new_system
                    }})
        # else:
        #     print(f"Unknown error occured. megaship {megaship_name} system {new_system}")
        else:   
            megaship_collection.insert_one({
                'name': megaship_name,
                'SYSTEM1': new_system if week == 1 else None,
                'SYSTEM2': new_system if week == 2 else None,
                'SYSTEM3': new_system if week == 3 else None,
                'SYSTEM4': new_system if week == 4 else None,
                'SYSTEM5': new_system if week == 5 else None,
                'SYSTEM6': new_system if week == 6 else None,
            })
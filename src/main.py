print("[0/4] Loading Imports, Please Stand By")
import zlib
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import zmq
import simplejson
import sys
import time
import datetime
from pymongo import MongoClient
import threading
import queue
import os

# Local

from megaships import add_megaship
from star_systems import add_system
from stations import add_station, alter_station_data
from constants import DATABASE_URI, EDDN_TIMEOUT, EDDN_URI, IGNORE_THESE, get_week_of_cycle, DATABASE_HOST, Megaship, StarSystem, Station

Base = sqlalchemy.orm.declarative_base()


"""
TABLES:

star_systems:

    system_name text
    latitude float
    longitude float
    height float
    state text (powerplay state)
    shortcode text (power shortcode)
    is_anarchy bool
    has_res_sites bool

stations:

    name text
    system text
    type text (Starport, Outpost, PlanetaryPort, Settlement, EngineerBase)

megaships: 
    name text pri key
    system1 text
    system2 text
    system3 text
    system4 text
    system5 text
    system6 text
"""





engine = None
try:
    print(f"[1/4] Connecting to EliteDB via {DATABASE_HOST}")
    engine = sqlalchemy.create_engine(DATABASE_URI)
    print("[1/4] Connected.")
except Exception as e:
    print(e)
    os.exit()
    

print(f"[2/4] Today is week {get_week_of_cycle()} in a 6-week cycle.")


# Create a queue to store messages
message_queue = queue.Queue()


# Ensure messages are properly removed from the message_queue
def count_messages_per_minute(q):
    global message_count
    message_count = 0
    while True:
        time.sleep(60 * 60)
        timestr = f"{datetime.datetime.now().date()} {datetime.datetime.now().time()}"
        open("mpm.txt", "a").write(f"{message_count},{timestr}\n")
        message_count = 0
        while not q.empty():
            q.get()
            message_count += 1


def main():
    time.sleep(5)
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    print(f"[2/4] Loaded")
    Session = sessionmaker(bind=engine)
    session = Session()
    subscriber.setsockopt(zmq.SUBSCRIBE, b"")
    subscriber.setsockopt(zmq.RCVTIMEO, EDDN_TIMEOUT)
    print(f"[3/4] EDDN Subscription Ready")

    # Start the message counter thread
    threading.Thread(
        target=count_messages_per_minute, daemon=True, args=(message_queue,)
    ).start()

    try:
        subscriber.connect(EDDN_URI)
        print(f"[4/4] Connected to EDDN via {EDDN_URI}")

        while True:
            try:
                __message = subscriber.recv()
                message_queue.put(__message)

                if __message == False:
                    subscriber.disconnect(EDDN_URI)
                    print("Disconneted from EDDN. Suspected downtime?")
                    break

                __message = zlib.decompress(__message)
                __json = simplejson.loads(__message)

                if "event" in __json["message"]:
                    match __json["message"]["event"]:
                        case "Docked":
                            economy = None
                            try:
                                economy = str(
                                    __json["message"]["StationEconomies"][0]["Name"]
                                )
                            except Exception:
                                economy = "$economy_None;"
                            economy = economy.replace("$economy_", "")
                            economy = economy.removesuffix(";")

                            system_name = str(__json["message"]["StarSystem"])
                            station_name = str(__json["message"]["StationName"])
                            station_type = str(__json["message"]["StationType"])
                            if (
                                economy == "Carrier"
                                or station_name == "System Colonisation Ship"
                                or station_type == "OnFootSettlement"
                                or station_name in IGNORE_THESE
                            ):
                                # print(f"ingored {station_name}")
                                continue

                            alter_station_data(
                                station_name,
                                system_name,
                                economy,
                                station_type,
                                session,
                            )

                        case "FSSSignalDiscovered":
                            for signal in __json["message"]["signals"]:
                                if "SignalType" in signal:
                                    if signal["SignalType"] == "ResourceExtraction":
                                        systemName = str(
                                            __json["message"]["StarSystem"]
                                        )
                                    elif signal["SignalType"] == "Megaship":
                                        megaship_name = str(signal["SignalName"])
                                        systemName = str(
                                            __json["message"]["StarSystem"]
                                        )
                                        add_megaship(megaship_name, systemName, session)
                                    elif signal["SignalType"] == "StationCoriolis":
                                        station_name = str(signal["SignalName"])
                                        systemName = str(
                                            __json["message"]["StarSystem"]
                                        )
                                        add_station(
                                            session,
                                            station_name,
                                            "Coriolis",
                                            systemName,
                                            "",
                                        )
                                    elif signal["SignalType"] == "Outpost":
                                        station_name = str(signal["SignalName"])
                                        systemName = str(
                                            __json["message"]["StarSystem"]
                                        )
                                        add_station(
                                            session,
                                            station_name,
                                            "Outpost",
                                            systemName,
                                            "",
                                        )
                                    elif signal["SignalType"] == "StationONeilOrbis":
                                        station_name = str(signal["SignalName"])
                                        systemName = str(
                                            __json["message"]["StarSystem"]
                                        )
                                        add_station(
                                            session,
                                            station_name,
                                            "Orbis",
                                            systemName,
                                            "",
                                        )
                                    elif signal["SignalType"] == "Ocellus":
                                        station_name = str(signal["SignalName"])
                                        systemName = str(
                                            __json["message"]["StarSystem"]
                                        )
                                        add_station(
                                            session,
                                            station_name,
                                            "Ocellus",
                                            systemName,
                                            "",
                                        )

                        case "FSDJump":
                            starPos = __json["message"]["StarPos"]
                            shortcode = ""
                            state = ""
                            if "PowerPlayState" in __json["message"]:
                                state = __json["message"]["PowerplayState"]
                                if "ControllingPower" in __json["message"] and state != "Unoccupied":
                                    power = __json["message"]["ControllingPower"]
                                
                                shortcode = ""
                                match power:
                                    case "Edmund Mahon":
                                        shortcode = "EMH"
                                    case "A. Lavigny-Duval":
                                        shortcode = "ALD"
                                    case "Aisling Duval":
                                        shortcode = "ASD"
                                    case "Yuri Grom":
                                        shortcode = "YRG"
                                    case "Pranav Antal":
                                        shortcode = "PRA"
                                    case "Denton Patreus":
                                        shortcode = "DPT"
                                    case "Jerome Archer":
                                        shortcode = "JRA"
                                    case "Nakato Kaine":
                                        shortcode = "NAK"
                                    case "Archon Delane":
                                        shortcode = "ARD"
                                    case "Li Yong-Rui":
                                        shortcode = "LYR"
                                    case "Felicia Winters":
                                        shortcode = "FLW"
                                    case "Zemina Torval":
                                        shortcode = "ZMT"
                                    case _:
                                        shortcode = ""

                            latitude = starPos[1]
                            longitude = starPos[0]
                            height = starPos[2]
                            system_name = __json["message"]["StarSystem"]
                            security = __json["message"]["SystemSecurity"]
                            isAnarchy = False
                            if security == "$GAlAXY_MAP_INFO_state_anarchy;":
                                isAnarchy = True
                            else:
                                isAnarchy = False

                            add_system(
                                session,
                                system_name,
                                latitude,
                                longitude,
                                height,
                                state,
                                shortcode,
                                isAnarchy,
                            )

            except zmq.ZMQError as e:
                print("ZMQSocketException: " + str(e))
                sys.stdout.flush()
                subscriber.disconnect(EDDN_URI)
                client.close()
                time.sleep(5)
    except zmq.ZMQError as e:#Exception as e:
        print("Error: " + str(e))
        sys.stdout.flush()
        client.close()
        time.sleep(5)
        return


main()

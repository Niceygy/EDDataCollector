print("[0/4] Loading Imports, Please Stand By")

# Packages
import math
import zlib
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import zmq
import simplejson
import sys
import time
import datetime
import traceback
import os

# Local

from megaships import add_megaship
from powers import PowerUpdate
from star_systems import update_system
from websocket import start_ws
from constants import (
    DATABASE_URI,
    EDDN_TIMEOUT,
    EDDN_URI,
    get_week_of_cycle,
    DATABASE_HOST,
    should_be_ignored,
    VALID_CLIENT_VERSION,
    MESSAGE_TIMEOUT,
)

"""
Database Connection
"""
Base = sqlalchemy.orm.declarative_base()


engine = None
try:
    engine = sqlalchemy.create_engine(DATABASE_URI)
    print(f"[1/4] Connected to EliteDB via {DATABASE_HOST}")
except Exception as e:
    print(e)
    os.exit()

"""
DateTime Logging
"""
powerplay_startdate = datetime.datetime(2024, 10, 31, 8)
now = datetime.datetime.now()

cycle = math.trunc((now - powerplay_startdate).days / 7)



print(f"[2/4] Megaship week {get_week_of_cycle()}/6. PowerPlay Cycle {cycle}.")


def is_message_valid(message: dict) -> bool:
    """Checks if the message has a valid gameversion & timestamp

    Args:
        message (dict): The message from EDDN to be checked

    Returns:
        bool: True if Valid, False if not
    """
    try:
        if "event" not in message["message"]:
            return False
        elif should_be_ignored(message):
            return False
        # client version
        client_version = message["header"]["gameversion"]
        client_version = str(client_version).split(".")
        good = False
        for i in range(len(client_version)):
            try:
                if int(client_version[i]) >= int(VALID_CLIENT_VERSION[i]):
                    good = True
                else:
                    return False
            except Exception:
                return False

        if good:
            # message age
            message_timestamp = datetime.datetime.strptime(
                message["message"]["timestamp"], "%Y-%m-%dT%H:%M:%SZ"
            )
            gateway_timestamp = datetime.datetime.strptime(
                message["header"]["gatewayTimestamp"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            time_difference = (
                message_timestamp - gateway_timestamp
            ).total_seconds() / 60
            if time_difference > MESSAGE_TIMEOUT:
                return False
            else:
                return True
        else:
            return False
    except Exception:
        return False


def main():
    time.sleep(5)
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    Session = sessionmaker(bind=engine, autoflush=True)
    session = Session()
    session.execute(sqlalchemy.text("DELETE FROM conflicts WHERE cycle < :cycle_t2"), {"cycle_t2": (cycle-2)})
    session.execute(sqlalchemy.text("UPDATE star_systems SET frequency = 1"))
    subscriber.setsockopt(zmq.SUBSCRIBE, b"")
    subscriber.setsockopt(zmq.RCVTIMEO, EDDN_TIMEOUT)
    # websocket_queue = start_ws()
    print(f"[3/4] EDDN Subscription Ready")

    try:
        subscriber.connect(EDDN_URI)
        print(f"[4/4] Connected to EDDN via {EDDN_URI}")

        while True:
            try:
                eddn_message = subscriber.recv()

                if eddn_message == False:
                    subscriber.disconnect(EDDN_URI)
                    print("Disconneted from EDDN. Suspected downtime?")
                    break

                eddn_message = zlib.decompress(eddn_message)
                __json = simplejson.loads(eddn_message)

                if is_message_valid(__json):
                    # websocket_queue._put(__json)
                    match __json["message"]["event"]:
                        case "FSSSignalDiscovered":
                            """
                            Signals - Stations & Megaships
                            """
                            for signal in __json["message"]["signals"]:
                                if "SignalType" in signal:
                                    # Megaships
                                    if signal["SignalType"] == "Megaship":
                                        megaship_name = str(signal["SignalName"])
                                        systemName = str(
                                            __json["message"]["StarSystem"]
                                        )
                                        add_megaship(megaship_name, systemName, session)
                                    elif str(signal["SignalType"]).__contains__(
                                        "$Warzone_Powerplay_"
                                    ):
                                        systemName = str(
                                            __json["message"]["StarSystem"]
                                        )
                                        print(f"PCZ: {systemName}")
                                        PowerUpdate.add_czs(system_name, session)

                        case "FSDJump":
                            """
                            Star system data - location, powers, ect
                            """
                            starPos = __json["message"]["StarPos"]
                            # location
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

                            update_system(
                                session,
                                # system data
                                system_name,
                                latitude,
                                longitude,
                                height,
                                isAnarchy,
                            )
                            PowerUpdate(__json, session)
                    session.commit()
                    session.flush()
            except zmq.ZMQError as e:
                print("ZMQSocketException: " + str(e))
                sys.stdout.flush()
                subscriber.disconnect(EDDN_URI)
                session.close()
                time.sleep(5)
    except Exception as e:
        print("Error: " + str(e))
        print(traceback.format_exc())
        sys.stdout.flush()
        session.close()
        subscriber.disconnect(EDDN_URI)
        return

if __name__ == "__main__":
    main()
    print(f"Closing script")
else:
    print(f"Script run as {__name__}. Please run as __main__")

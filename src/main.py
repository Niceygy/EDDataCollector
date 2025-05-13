print("[0/4] Loading Imports, Please Stand By")

# Packages
import zlib
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import zmq
import simplejson
import sys
import time
import datetime
import os
import math

# Local

from megaships import add_megaship
from powers import update_power_data
from star_systems import update_system
# from stations import add_station, alter_station_data
from constants import (
    DATABASE_URI,
    EDDN_TIMEOUT,
    EDDN_URI,
    get_week_of_cycle,
    DATABASE_HOST,
    power_full_to_short,
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
cycle = (now - powerplay_startdate).days / 7
cycle = math.trunc(cycle)

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
        # client version
        client_version = message["header"]["gameversion"]
        client_version = str(client_version).split(".")
        good = False
        for i in range(len(client_version)):
            try:
                if int(client_version[i]) >= int(VALID_CLIENT_VERSION[i]):
                    good = True
                else:
                    good = False
            except Exception:
                good = False
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
    subscriber.setsockopt(zmq.SUBSCRIBE, b"")
    subscriber.setsockopt(zmq.RCVTIMEO, EDDN_TIMEOUT)
    print(f"[3/4] EDDN Subscription Ready")

    try:
        subscriber.connect(EDDN_URI)
        print(f"[4/4] Connected to EDDN via {EDDN_URI}")

        while True:
            try:
                __message = subscriber.recv()

                if __message == False:
                    subscriber.disconnect(EDDN_URI)
                    print("Disconneted from EDDN. Suspected downtime?")
                    break

                __message = zlib.decompress(__message)
                __json = simplejson.loads(__message)

                if is_message_valid(__json):
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
                                    
                        case "FSDJump":
                            """
                            Star system data - location, powers, ect
                            """
                            starPos = __json["message"]["StarPos"]
                            shortcode = ""
                            state = ""
                            if "PowerplayState" in __json["message"]:
                                state = __json["message"]["PowerplayState"]
                                if (
                                    "ControllingPower" in __json["message"]
                                    and state != "Unoccupied"
                                ):
                                    power = __json["message"]["ControllingPower"]
                                elif "Powers" in __json["message"]:
                                    power = __json["message"]["Powers"][0]

                            try:
                                shortcode = power_full_to_short(power)
                            except Exception:
                                None

                            # Power Parser - is it in conflict?
                            power_conflict = False
                            power_opposition = ""
                            if "PowerplayConflictProgress" in __json["message"]:
                                conflict_progress = sorted(
                                    __json["message"]["PowerplayConflictProgress"],
                                    key=lambda x: x["ConflictProgress"],
                                    reverse=True,
                                )
                                if len(conflict_progress) > 0 and conflict_progress[0]['ConflictProgress'] > 0.2:
                                    shortcode = power_full_to_short(
                                        conflict_progress[0]["Power"]
                                    )
                                    if len(conflict_progress) > 1 and conflict_progress[1]['ConflictProgress'] > 0.1:
                                        power_opposition = power_full_to_short(
                                            conflict_progress[1]["Power"]
                                        )
                                        power_conflict = True

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
                            update_power_data(
                                system_name=system_name,
                                shortcode=shortcode,
                                state=state,
                                power_conflict=power_conflict,
                                conflict_opposing=power_opposition,
                                session=session,
                            )
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
        sys.stdout.flush()
        session.close()
        time.sleep(5)
        return


main()

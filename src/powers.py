from datetime import datetime
import math
from typing import Tuple
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker as sm
from constants import PowerData, power_full_to_short


class PowerUpdate:
    def __init__(self, __json: dict, session: sm):
        self.update_power_data(__json, session)
        return

    def is_in_war(self, __json: dict):
        """Checks if a system is in the contested state

        Args:
            __json (dict): the full json message

        Returns:
            shortcode, power_conflict, power_opposition
             (winning power, is system in war?, power in second)
        """
        # Power Parser - is it in conflict?
        power_conflict = False
        power_opposition = ""
        shortcode = ""
        if "PowerplayConflictProgress" in __json["message"]:
            powerConflictProgresses = []
            for item in __json["message"]["PowerplayConflictProgress"]:
                if float(item['ConflictProgress']) < 0.001:
                    None
                else:
                    powerConflictProgresses.append(
                        {
                            "progress": float(item["ConflictProgress"]),
                            "shortcode": power_full_to_short(item["Power"]),
                        }
                    )
                # e.g [0.115, "ALD"]

            isSorted = False
            while not isSorted:
                isSorted = True
                for i in range(len(powerConflictProgresses) - 1):
                    if powerConflictProgresses[i]['progress'] < powerConflictProgresses[i+1]['progress']:
                        _temp = powerConflictProgresses[i]
                        powerConflictProgresses[i] = powerConflictProgresses[i+1]
                        powerConflictProgresses[i+1] = _temp
                        isSorted = False
                        continue
                    else:
                        isSorted = True
                        continue
                                
            if len(powerConflictProgresses) > 0 and powerConflictProgresses[0]['progress'] > 0.2:
                    shortcode = powerConflictProgresses[0]["shortcode"]
                    if shortcode == '':
                        None
                
            if len(powerConflictProgresses) > 1 and powerConflictProgresses[1]['progress'] > 0.1:
                    power_opposition = powerConflictProgresses[1]["shortcode"]
                    power_conflict = True
                    
        if shortcode == power_opposition and power_conflict == True:
            power_conflict = False
        return shortcode, power_conflict, power_opposition


    def parse(self, __json: dict) -> Tuple[str, str, str]:
        """Returns the basic system info

        Args:
            __json (dict): message from eddn

        Returns:
            system_name (str), shortcode (str), state (str)
        """
        system_name = __json['message']['StarSystem']
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
        return system_name, shortcode, state

    def update_power_data(
        self,
        __json: dict,
        session: sm,
    ) -> None:
        """Updates the power data for the system

        Args:
            __json (dict): message from eddn
            session (sm): database session
        """
        system_name, shortcode, state = self.parse(__json)
        system_name = str(system_name).replace("'", ".")
        if state == "":
            # we only want powerplay systems!
            return

        entry = (
            session.query(PowerData)
            .filter(and_(PowerData.system_name == system_name))
            .first()
        )
        
        shortcode, is_in_conflict, conflict_opposition = self.is_in_war(__json)

        if entry is None:
            if is_in_conflict:
                session.add(
                    PowerData(
                        system_name=system_name,
                        state=state,
                        shortcode=shortcode,
                        war=True,
                        war_start=self.powerplay_cycle(),
                        opposition=conflict_opposition,
                    )
                )
            else:
                session.add(
                    PowerData(
                        system_name=system_name,
                        state=state,
                        shortcode=shortcode,
                    )
                )
        else:
            if (
                entry.war_start is not None
                and entry.war_start < (self.powerplay_cycle() - 2)
                and entry.war
            ):
                entry.war = False
                entry.war_start = None
                entry.opposition = None
            elif not entry.war and is_in_conflict:
                # war not in db, but is in power_conflict
                entry.war = is_in_conflict
                entry.war_start = self.powerplay_cycle()
                entry.opposition = conflict_opposition

            if entry.state != state:
                entry.state = state
                entry.shortcode = shortcode

            session.commit()
        return

    def powerplay_cycle(self) -> int:
        """
        Returns the current powerplay cycle number
        """
        # 31 oct '24
        powerplay_startdate = datetime(2024, 10, 31, 8)
        now = datetime.now()

        cycle = (now - powerplay_startdate).days / 7

        return math.trunc(cycle)

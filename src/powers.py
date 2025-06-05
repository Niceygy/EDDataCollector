from datetime import datetime
import math
from typing import Tuple
from sqlalchemy import and_, delete
from sqlalchemy.orm import sessionmaker as sm
from constants import PowerData, power_full_to_short, Conflicts


class PowerUpdate:
    def __init__(self, __json: dict, session: sm):
        self.update_power_data(__json, session)
        return

    def add_czs(self, system_name, session: sm):
        system_name = str(system_name).replace("'", ".")
        if system_name == "":
            return

        entry = (
            session.query(Conflicts)
            .filter(and_(Conflicts.system_name == system_name))
            .first()
        )

        if entry is None:
            return
        # other funcs will deal with this
        else:
            if not entry.has_czs:
                entry.has_czs = True
            session.commit()

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
                if float(item["ConflictProgress"]) < 0.001:
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
                    if (
                        powerConflictProgresses[i]["progress"]
                        < powerConflictProgresses[i + 1]["progress"]
                    ):
                        _temp = powerConflictProgresses[i]
                        powerConflictProgresses[i] = powerConflictProgresses[i + 1]
                        powerConflictProgresses[i + 1] = _temp
                        isSorted = False
                        continue
                    else:
                        isSorted = True
                        continue

            if (
                len(powerConflictProgresses) > 0
                and powerConflictProgresses[0]["progress"] > 0.3
            ):
                shortcode = powerConflictProgresses[0]["shortcode"]
                if shortcode == "":
                    None

            if (
                len(powerConflictProgresses) > 1
                and powerConflictProgresses[1]["progress"] > 0.3
            ):
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
        system_name = __json["message"]["StarSystem"]
        shortcode = ""
        state = ""
        if "PowerplayState" in __json["message"]:
            state = __json["message"]["PowerplayState"]
            if "ControllingPower" in __json["message"] and state != "Unoccupied":
                power = __json["message"]["ControllingPower"]
            elif "Powers" in __json["message"]:
                power = __json["message"]["Powers"][0]
            try:
                shortcode = power_full_to_short(power)
            except Exception:
                None
        return system_name, shortcode, state
    
    def corrected_control_pts(self, state: str, progress: float) -> float:
        """Corrects the control points for use in the db

        Args:
            state (str): system state
            progress (float): progress from journal

        Returns:
            float: Corrected control pts
        """
        if progress > 4000:
            if state == "Exploited":
                scale = 349999
            elif state == "Fortified":
                scale = 650000
            elif state == "Stronghold":
                scale = 1000000
            else: # must be "Unoccupied", never reached
                scale = 120000
            progress -= 4294967296 / scale
        return progress

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
        journal_control_pts = __json['message'].get('PowerplayStateControlProgress', 0)
        if state == "":
            # we only want powerplay systems!
            return

        entry = (
            session.query(PowerData)
            .filter(and_(PowerData.system_name == system_name))
            .first()
        )

        is_in_conflict = False
        conflict_opposition = ""
        if 'PowerPlayState' in __json["message"] and __json['message']['PowerPlayState'] != "Unoccupied":
            shortcode, is_in_conflict, conflict_opposition = self.is_in_war(__json)
        

        if entry is None:
            if is_in_conflict:
                session.add(
                    PowerData(
                        system_name=system_name,
                        state="War",
                        shortcode=shortcode,
                        control_points=self.corrected_control_pts(state, journal_control_pts),
                        points_change=0
                    )
                )
                session.add(
                    Conflicts(
                        system_name=system_name,
                        first_place=shortcode,
                        second_place=conflict_opposition,
                        has_czs=False,
                        cycle=self.powerplay_cycle(),
                    )
                )
            else:
                session.add(
                    PowerData(
                        system_name=system_name,
                        state=state,
                        shortcode=shortcode,
                        control_points=self.corrected_control_pts(state, journal_control_pts),
                        points_change=0
                    )
                )
        else:
            if entry.state == "War" and is_in_conflict:
                self.update_war(
                    system_name=system_name, first=shortcode, second=conflict_opposition, session=session
                )
            elif entry.state == "War" and not is_in_conflict:
                self.remove_war(system_name, session)
            elif entry.state != state:
                entry.state = state
                entry.shortcode = shortcode
            if 'PowerplayStateControlProgress' in __json['message']: #_PowerUpdate__json['message']['PowerplayStateControlProgress']
                if entry.control_points is None: entry.control_points = self.corrected_control_pts(state, journal_control_pts)
                points_change = abs(entry.control_points - self.corrected_control_pts(state, journal_control_pts))
                entry.points_change = points_change
                # print(f"Updated {system_name} to {entry.points_change} points change (state {entry.state})")
                # print(f"    (corrected pts={self.corrected_control_pts(state, journal_control_pts)})")
                # print(f"    (journal pts={journal_control_pts})")
                # print(f"    ({__json['message']['PowerplayStateControlProgress']})")
                # print(" ")


            session.commit()
        return

    def update_war(
        self, first: str, second: str, system_name: str, session: sm
    ) -> None:
        """Updates a currently active conflict

        Args:
            first (str): Winning power
            second (str): Second place power
            system_name (str): system name
            session (sm): Database session
        """
        entry = (
            session.query(Conflicts)
            .filter(and_(Conflicts.system_name == system_name))
            .first()
        )

        if entry is None:
            session.add(
                Conflicts(
                    system_name=system_name,
                    first_place=first,
                    second_place=second,
                    has_czs=False,
                    cycle=self.powerplay_cycle(),
                )
            )
        else:
            entry.first_place = first
            entry.second_place = second

        session.commit()

        return

    def remove_war(self, system_name: str, session: sm) -> None:
        """Removes a war from the conflicts table and
        updates the corresponding record on the powerdata table

        Args:
            system_name (str): System Name
            session (sm): Database Session
        """
        victor = (
            session.query(Conflicts)
            .filter(and_(Conflicts.system_name == system_name))
            .first()
        )
        
        if victor is None:
            return
        else:
            victor = victor.first_place

        powerdata_entry = (
            session.query(Conflicts)
            .filter(and_(Conflicts.system_name == system_name))
            .first()
        )
        if powerdata_entry is None:
            session.add(
                PowerData(system_name=system_name, state="Exploited", shortcode=victor)
            )
        else:
            powerdata_entry.state = "Exploited"
            powerdata_entry.shortcode = victor
            
        delete(Conflicts).where(Conflicts.system_name == system_name)

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

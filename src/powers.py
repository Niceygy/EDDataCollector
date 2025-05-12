from datetime import datetime
import math
from sqlalchemy import and_, func
from sqlalchemy.orm import sessionmaker as sm
from constants import PowerData


def update_power_data(
    system_name: str, shortcode: str, state: str, power_conflict: bool, session: sm
):
    system_name = str(system_name).replace("'", ".")
    if state == "":
        # we only want powerplay systems!
        return

    entry = (
        session.query(PowerData)
        .filter(and_(PowerData.system_name == system_name))
        .first()
    )

    if entry is None:
        if power_conflict:
            session.add(
                PowerData(
                    system_name=system_name,
                    state=state,
                    shortcode=shortcode,
                    war=True,
                    war_start=powerplay_cycle(),
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
        if entry.war_start is not None and entry.war_start < (powerplay_cycle() - 2) and entry.war:
            entry.war = False
        elif not entry.war and power_conflict:
            #war not in db, but is in power_conflict
            entry.war = power_conflict
            entry.war_start = powerplay_cycle()

        if entry.state != state:
            entry.state = state
            entry.shortcode = shortcode
        
        session.commit()
    return


def powerplay_cycle() -> int:
    """
    Returns the current powerplay cycle number
    """
    # 31 oct '24
    powerplay_startdate = datetime(2024, 10, 31, 8)
    now = datetime.now()

    cycle = (now - powerplay_startdate).days / 7

    return math.trunc(cycle)
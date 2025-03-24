from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker as sm
from constants import PowerData


def update_power_data(
    system_name: str, shortcode: str, state: str, controlPoints: str, session: sm
):
    system_name = str(system_name).replace("'", ".")

    entry = (
        session.query(PowerData)
        .filter(and_(PowerData.system_name == system_name))
        .first()
    )

    if entry is None:
        new_powerdata = PowerData(
            system_name=system_name,
            state=state,
            shortcode=shortcode,
            controlPointsStart=0,
            controlPointsLatest=controlPoints,
        )
        session.add(new_powerdata)
    else:
        if entry.state != '':
            i = 0
        if entry.state != state:
            entry.state = state
            entry.shortcode = shortcode
            entry.controlPointsStart = controlPoints
        else:
            entry.controlPointsStart = controlPoints
    return

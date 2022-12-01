import os
import datetime
import time


def str_to_unix(date_str: str, fmt: str = "%Y-%m-%dT%H:%M:%S") -> int:
    date_datetime = datetime.datetime.strptime(date_str, fmt)
    return int(time.mktime(date_datetime.timetuple()))


def unix_to_str(unix_timestamp: int, fmt: str = "%Y-%m-%dT%H:%M:%S") -> str:
    return datetime.datetime.fromtimestamp(int(unix_timestamp))


def repeat_dates(
    date_str_list: list[str], num_weeks: int, fmt: str = "%Y-%m-%dT%H:%M:%S"
) -> list[str]:
    """Extend a list of date strings to repeat for num_weeks."""
    extended_dates = []
    for date_str in date_str_list:
        date_datetime = datetime.datetime.strptime(date_str, fmt)
        extended_dates += [
            datetime.datetime.strftime(date_datetime + datetime.timedelta(weeks=i), fmt)
            for i in range(num_weeks)
        ]
    return extended_dates


def notify(title: str, description: str, duration: int = 4) -> None:
    """Send a notification for duration secs with title and description.

    Display a notification for input duration seconds.
    Depending on the notification manager of the system, duration may not
    actually work.

    Parameters
    ----------
    title : str
        Title of notification
    description : str
        Description of the notification
    duration : int
        How many *seconds* to display the notification for
    """
    t = duration * 1000
    try:
        os.system(f"notify-send -t {t} '{title}' '{description}'")
    except:
        print("Unable to send notifications! Ensure notify-send is in path.")

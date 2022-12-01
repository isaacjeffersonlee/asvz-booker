import datetime
import requests
from helpers import repeat_dates, unix_to_str
from scraper import AsvzScraper
from enroller import enroll

# TODO: Test with fitness
# TODO: Add docstrings


def main():
    num_weeks = 3
    lesson_datetimes = {
        "Brazilian Jiu Jitsu": repeat_dates(
            ["2022-11-29T12:15:00", "2022-12-02T17:00:00"], num_weeks=num_weeks
        ),
        "Fussball": repeat_dates(["2022-11-30T19:00:00"], num_weeks=num_weeks),
        # "Tischtennis": repeat_dates(["2022-11-18T19:45:00"], num_weeks=num_weeks),
        # "Standard/Latin Tänze": repeat_dates(["2022-11-25T12:00:00"], num_weeks=10),
    }
    with requests.Session() as session:
        scraper = AsvzScraper(
            lesson_datetimes=lesson_datetimes,
            session=session,
        )
        lessons_df = scraper.get_lessons_df()

    while not lessons_df.empty:
        # Note: lessons_df is sorted by online enrollment time, so
        # the next enrollment time is just the first row in the df.
        # (We assume no clashes in enrollment times).
        lessons_df.reset_index(inplace=True, drop=True)
        lessons_df_t = lessons_df.T
        next_sport = lessons_df_t.pop(0)  # Pop the first row
        lessons_df = lessons_df_t.T
        next_sport["oe_from_date_stamp"]
        next_oe_from_date = datetime.datetime.fromtimestamp(next_sport["oe_from_date_stamp"])
        # Ignore dates where we have missed the enrollment time
        if datetime.datetime.now() < next_oe_from_date:
            print("")
            print("======================================================================")
            print(f"Waiting to enroll for {next_sport['sport_name']}")
            print(f"Taking place @ {next_sport['location']}, {unix_to_str(next_sport['from_date_stamp'])}")
            print(f"Enrollment time: {unix_to_str(next_sport['oe_from_date_stamp'])}")
            print(f"Instructor(s): {next_sport['instructor_name']}")
            print(f"Url: {next_sport['url']}")
            print("======================================================================")
            print("")
            enrollment_time = next_sport["oe_from_date_stamp"]
            enroll(lesson_url=next_sport["url"], enrollment_time=enrollment_time, lesson_name=next_sport["sport_name"])


if __name__ == "__main__":
    main()

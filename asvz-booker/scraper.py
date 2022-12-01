import requests
from helpers import unix_to_str, str_to_unix, repeat_dates
import os
import pandas as pd


class AsvzScraper:
    def __init__(
        self,
        lesson_datetimes: dict[str, list[str]],
        session: requests.Session,
    ):
        self.lesson_datetimes = lesson_datetimes
        self.lesson_list = lesson_datetimes.keys()
        self._session = session

    def _request_lessons(
        self, limit: int = 1000, tids: list[str] = []
    ) -> requests.Response:
        params = {"_format": "json", "limit": limit, "offset": 0}
        params.update({f"f[{i}]": f"sport:{tid}" for i, tid in enumerate(tids)})
        r = self._session.get(
            url="https://asvz.ch/asvz_api/event_search",
            params=params,
        )
        assert r.status_code == 200, f"Non 200 status: {r.status_code}"
        return r

    def _parse_lesson_tids(self, r: requests.Response) -> dict[str, int]:
        facets = r.json()["facets"]
        sports_facet = {}
        for facet in facets:
            if facet["id"] == "sport":
                sports_facet = facet
        if not sports_facet:
            raise EOFError("Error: No facet with id: sport")

        tid_df = pd.DataFrame.from_dict(sports_facet["terms"])
        # If we leave lesson_list as an empty list, then all
        # lessons will be returned.
        if self.lesson_list:
            tid_df = tid_df.loc[tid_df["label"].isin(self.lesson_list)]
        tid_df = tid_df[["label", "tid"]]
        tid_df.set_index("label", inplace=True)
        return tid_df.to_dict()["tid"]

    def get_lessons_df(self, update: bool = False) -> pd.DataFrame:
        pickle_path = "Data/lessons_df.pkl"
        if not os.path.exists(pickle_path) or update:
            print("Updating lesson information...")
            # First make a small request for all sports to get unique ids
            r = self._request_lessons(limit=100)
            tid_dict = self._parse_lesson_tids(r)
            r = self._request_lessons(limit=500, tids=tid_dict.values())
            lessons_df = pd.DataFrame.from_dict(r.json()["results"])
            lessons_df.to_pickle(pickle_path)
        else:
            lessons_df = pd.read_pickle(pickle_path)

        # Loop over each sport and get the index of the lessons which take place
        # at the times specified in lesson_datetimes.
        # We have to do this in a loop because we could have different sports
        # with the same from_date_stamps.
        idx_to_keep = pd.Index([])
        for sport_name, date_str_list in self.lesson_datetimes.items():
            lesson_timestamps = pd.Series(map(str_to_unix, date_str_list))
            idx = lessons_df.loc[
                (lessons_df["from_date_stamp"].isin(lesson_timestamps))
                & (lessons_df["sport_name"] == sport_name)
            ].index
            idx_to_keep = idx_to_keep.append(idx)
        lessons_df = lessons_df.iloc[idx_to_keep]
        lessons_df.sort_values(by="oe_from_date_stamp", inplace=True)
        lessons_df.reset_index(inplace=True, drop=True)
        return lessons_df


def main():
    lesson_datetimes = {
        "Brazilian Jiu Jitsu": repeat_dates(
            ["2022-11-22T12:15:00", "2022-12-02T17:00:00"], num_weeks=10
        ),
        "Fussball": repeat_dates(["2022-11-23T19:00:00"], num_weeks=10),
        "Tischtennis": repeat_dates(["2022-11-18T19:45:00"], num_weeks=10),
        # "Standard/Latin Tänze": repeat_dates(["2022-11-25T12:00:00"], num_weeks=10),
    }
    with requests.Session() as session:
        scraper = AsvzScraper(
            lesson_datetimes=lesson_datetimes,
            session=session,
        )
        lessons_df = scraper.get_lessons_df()
        print(lessons_df)


if __name__ == "__main__":
    main()

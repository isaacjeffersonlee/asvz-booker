import requests
import time
import datetime
from typing import Union, Optional
from asvz_details import asvz_id, asvz_password

# TODO: When migrating to amazon EC2 Server (change client id and others accordingly)


def get_bearer(s: requests.Session) -> str:
    """
    Get the bearer token str.

    This is required for sending any requests where
    the user would normally have to login.

    Parameters
    ----------
    s : requests.Session
        The requests session to use to send requests with.
        Note: the user needs to have already sent a login request
        so that the sessions cookies get populated.

    Returns
    -------
    str
        The bearer token to be used in other requests.
    """
    url = "https://auth.asvz.ch/connect/authorize"
    querystring = {
        "client_id": "55776bff-ef75-4c9d-9bdd-45e883ec38e0",
        "redirect_uri": "https://schalter.asvz.ch/tn/assets/oidc-login-redirect.html",
        "response_type": "id_token token",
        "scope": "openid profile tn-api tn-apiext tn-auth tn-hangfire",
        "state": "229b87bc5d2e491386f17feab7dec2ad",  # Can be any number (I think)
        "nonce": "1531ccb396a24377e971eadbd58b9b3d",  # Also can be any number
    }
    payload = {}
    headers = {
        # Cookies should be automatically set in the requests session object by first sending a login request
        # "cookie": ".AspNetCore.Antiforgery.FjrndYkeEns=CfDJ8PwLmQnAAftGq6dNrCn4IKJWFqqmMczwKw2Oe2mJcFaHiaSeBSVGDa1ZQ6xMHNLhkzX-dnmuW6EqMejzb1-IdOQ70TPNeKi9JV50LDWplcc9Fe65-t9t5X1MQcrY_uwgTPXsJvbOPulXEup7ll78YOk; idsrv.session=82ebd9f5772cf643b256d8245cd53698; .AspNetCore.Identity.Application=CfDJ8PwLmQnAAftGq6dNrCn4IKKpckbBNdFLoSBYHuz1XuFK0LBTSZotNAok8O8GzPHebi54vVG89qAn8OR8GTG4SSyFWF62lGOTkbRqMj7HLXHeYIK6U2nTYUBzpeXUp4B3b_OCOYbD8a0R5NW7x6jEx-v43jNfgMwlN84aDwOeJhyUiRCMv-b-qUctaGck6WT2kXsYjfARSQToxAhYYvjrCDEVC3Z9NGpUEHB8y-4XV193WUGfdx0QGz78F7H5G7DwX2aoFmL2B0b9BKFMMElkirHDIZA9Mt_xhiqybW7A0z-1ppN42x5kuCQVOQhD14J7hDzT_wxrGTrrcsJpwRpPWrobSJQ9Lzvgz3maMfZfK1i0SkMiO67EKg7bnVkWnkEskANue2xvwLaHcJYEG88ue0AT6eze7UkioatwGRSX1Vg30eikxw1oc6mc0jXk8oPTAdxB3OEvXxpkQNx0zJ1SDPr5_JseURw0UMc40j9OpIwOLk36wlWaC3CiaMt59PUp_oJdtCyYHsCSWE8N11qSy9dbPK_ISbM9mPl5ZGX4mLZhqxKl6FpxE5gJC3HMpgKcIX_ZKo-FgvF8mhAFrGyIsMSpXJ3ZjoTaI1DJ8KgRBb7KNH9iuDTh9R6HgYJqAVZFQAIlYeq7IxkT9lZW62a3UtMKbvNGVim1KQ5kL_9nCMMwPy_UfRn0xA9mrjpOEwip-mdz5zyXUEL2xDou9l7Hd2TtMz0vHNrNj9biPppFJj7t49bRA7jyZGkckeZRQMuX5ivwopCa_08PXDbB99-Y3yMcduN22K9aY0n9_i2KuFJB36TD2snXWNoJ7OUD4eo5Kw54N2hA-DuSMZ1xaP0whzeeSOEp2Tbo4JsJ1oRHX0ppMMJ4_LseRVfHTXnuI0aZMA0qyMj4pPuAM8sjtx5xz96fCZ2UIo3iBg6kvCFrZUWYiitAStceeuIea3V6Mal0EwX6V6YaxyzecLGvrE_DB-m2Sk7ihr61aBdrGJHhhdxe",
        "authority": "auth.asvz.ch",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "dnt": "1",
        "referer": "https://schalter.asvz.ch/",
        "sec-ch-ua": '"Not;A=Brand";v="99", "Chromium";v="106"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    }

    r = s.get(
        url,
        data=payload,
        headers=headers,
        params=querystring,
        allow_redirects=False,
    )
    for header in r.headers["location"].split("&"):
        if "access_token" in header:
            access_token = header.split("=")[-1]
            return access_token


def login(
    s: requests.Session, asvz_id: Union[str, int], asvz_password: str
) -> requests.Response:
    """
    Send a login request to the ASVZ server.

    This method is required to be called before sending
    any enrollment requests because it populates the session
    cookies.

    Parameters
    ----------
    s : requests.Session
        Session object in which the cookies get stored.
    asvz_id : Union[str, int]
        Users ASVZ id, can be found in their asvz details page.
    asvz_password : str
        Users ASVZ password, used to login.

    Returns
    -------
    requests.Response
        Response object, returned from the login request.
        Only really useful for querying status code.
    """
    url = "https://auth.asvz.ch/Account/Login"
    payload = {
        "AsvzId": asvz_id,
        "Password": asvz_password,
        "__RequestVerificationToken": "CfDJ8PwLmQnAAftGq6dNrCn4IKJS_YRlsRMh0d8BBVxV4Q75MAmdBx3lYOqh3BtJ98JX9oJ9IywHMmY1_NFhGSXUCCEDoaBSadbumr1U94oi1rJkPEr2Cgk6Qtpv3ODlyhSx8vU_Htn8zMMIua4FvWHo1iw",
    }
    headers = {
        "cookie": ".AspNetCore.Antiforgery.FjrndYkeEns=CfDJ8PwLmQnAAftGq6dNrCn4IKLUyFIa2p_uH6nSCL_9W2Q8UQvKnIoCs0PQs1YAE0OKp3TKLmiLVtQcYtSpxg9hBGSabkz8FlPcoUkMg4PdTyfDlHmG2jzq1pNOSKHH2TeynC4bhDa_x6GYDWCP6OjZf4M",
        "authority": "auth.asvz.ch",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "dnt": "1",
        "origin": "https://auth.asvz.ch",
        "referer": "https://auth.asvz.ch/account/login",
        "sec-ch-ua": '"Not;A=Brand";v="99", "Chromium";v="106"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    }

    return s.post(url, data=payload, headers=headers, allow_redirects=False)


def request_enroll(s: requests.Session, referer_url: str) -> requests.Response:
    """
    Send an enrollment request to the ASVZ server.

    Sends a post request to enroll a user for the sport
    found at the referer_url url.
    NOTE: The user must first have sent a login request
    so that the authentication cookies get generated in
    the session object.

    Parameters
    ----------
    s : requests.Session
        Requests session used to login, therefore containing
        the correct authentication cookies.
    referer_url : str
        The url of the ASVZ web page for the lesson a user
        wishes to enroll for.
        NOTE: Each sport has a separate page for each different
        time the sport takes place, E.g Jiu Jitsu has a separate
        web page for the Monday 12AM session.

    Returns
    -------
    requests.Response
        The Requests response object.
        Only returned so that we can query the status
        of the request.
    """
    lesson_id = referer_url.split("/")[-1]
    enrollment_url = (
        f"https://schalter.asvz.ch/tn-api/api/Lessons/{lesson_id}/Enrollment"
    )
    querystring = {"?t": str(int(time.time() * 1000))}
    payload = {}
    headers = {
        "authority": "schalter.asvz.ch",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "authorization": f"Bearer {get_bearer(s)}",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://schalter.asvz.ch",
        "referer": referer_url,
        "sec-ch-ua": '"Not;A=Brand";v="99", "Chromium";v="106"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    }

    return s.post(enrollment_url, json=payload, headers=headers, params=querystring)


def enroll(
    lesson_url: str,
    enrollment_time: Union[str, int],
    lesson_name: Optional[str] = ""
) -> None:
    """
    Enroll a user for a specific lesson at a specific time.

    Wrapper function that combines all of the other methods
    in this module to enroll a user for a specific lesson
    with webpage lesson_url at enrollment_time.
    Sleeps in a loop until the enrollment time is close,
    then decreases the length of sleep accordingly.
    Also prints out timing information.
    Once the current time hits enrollment_time, logs in
    and sends an enrollment request to enroll the user.

    Parameters
    ----------
    lesson_url : str
        The url of the ASVZ web page for the lesson a user
        wishes to enroll for.
        NOTE: Each sport has a separate page for each different
        time the sport takes place, E.g Jiu Jitsu has a separate
        web page for the Monday 12AM session.
    enrollment_time : Union[str, int]
        The time that the enrollment period begins.
        This can either be in int unix timestamp format
        or as a human readable str, in the format:

            '%Y-%m-%dT%H:%M:%S.%f'

    lesson_name : Optional[str]
        String name of the lesson to enroll for.
        This argument is only used for printing,
        so is optional.
    """
    if isinstance(enrollment_time, str):
        enrollment_time = datetime.datetime.strptime(
            enrollment_time, "%Y-%m-%dT%H:%M:%S.%f"
        )
    else:  # int or np.int64
        enrollment_time = datetime.datetime.fromtimestamp(enrollment_time)

    print(f"Time is: {datetime.datetime.now()}")
    print("Testing login request...")
    time_before_login = datetime.datetime.now()

    with requests.Session() as session:
        r = login(session, asvz_id=asvz_id, asvz_password=asvz_password)
        print(f"Test login request status: {r.status_code}")
    time_after_login = datetime.datetime.now()
    login_time = (time_after_login - time_before_login).total_seconds()
    print(f"Login took: {login_time}s")
    print("Entering wait loop...")
    # Blocking while loop
    while datetime.datetime.now() < enrollment_time - datetime.timedelta(seconds=30):
        current_time = datetime.datetime.now()
        print("----------------------------------------------------------------------")
        if lesson_name:
            print(f"Waiting to enroll for: {lesson_name} @ {enrollment_time}")
        print(f"Current time: {current_time}")
        print(f"Time until enrollment: {enrollment_time - current_time}")
        print("----------------------------------------------------------------------")
        print("")
        time.sleep(5)

    print(f"Broken out of wait loop, time is: {datetime.datetime.now()}")
    print("Sending login request...")
    with requests.Session() as session:
        r = login(session, asvz_id=asvz_id, asvz_password=asvz_password)
        print(f"Login request status: {r.status_code}")
        print(f"Login request status: {r.status_code}")
        while True:
            time.sleep(0.01)
            if datetime.datetime.now() >= enrollment_time:
                print("Sending enroll request...")
                r = request_enroll(session, lesson_url)
                print(f"Enrollment request sent, response status: {r.status_code}")
                break
    print("Finished!")


def main():
    lesson_url = "https://schalter.asvz.ch/tn/lessons/367674"
    enrollment_time = "2023-12-30T19:00:00.013"
    enroll(lesson_url=lesson_url, enrollment_time=enrollment_time)
    # with requests.Session() as session:
    #     r = login(session, asvz_id, asvz_password)
    #     print(r.status_code)


if __name__ == "__main__":
    main()

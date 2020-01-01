from typing import List
from os import path
from settings import *
from fb_user import FBUser
import exceptions
import configparser
from ics import Calendar
from fb2cal.src import fb2cal
import random
from datetime import datetime

""" 
Methods to check the following files existence:
- account_details.txt
- download_date.txt
- config.ini
- birthdays.ics
"""


def account_details_file_exists() -> bool:
    """Check if account details file exists"""
    return path.exists(config.account_details_path)


def fb2cal_config_exists() -> bool:
    """Check if fb2cal config.ini file exists"""
    return path.exists(config.config_dir)


def ics_file_exists() -> bool:
    """Check if ics file exists"""
    return path.exists(config.calendar_dir)


def download_date_file_exists() -> bool:
    """Check if download_date.txt file exists"""
    return path.exists(config.download_date)


""" 
Methods to parse, create, read from and write to the following files:
- account_details.txt
- download_date.txt
- funny_birthday_wish_path.txt
- serious_birthday_wish_path.txt
- config.ini
- birthdays.ics
"""


def read_account_details() -> List[str]:
    """ Read username and password from
    account_details.txt file and return them as a list."""
    f = open(config.account_details_path, "r")
    account_details = f.read().splitlines()
    f.close()
    return account_details


def set_fb2cal_config_fb_email_fb_pass(login: str, password: str) -> None:
    """Update fb_email and fb_pass in fb2cal config.ini file"""
    configuration = configparser.ConfigParser()
    configuration.read(config.config_dir)
    configuration.set("AUTH", "fb_email", login)
    configuration.set("AUTH", "fb_pass", password)
    with open(config.config_dir, "w") as f:
        configuration.write(f)


def parse_ics() -> Calendar:
    """ Parse a calendar from ics format"""
    with open(config.calendar_dir, 'rb') as g:
        return Calendar(g.read().decode())


def download_birthday_calendar() -> None:
    """ Gets a birthday calendar from Facebook and saves it as an ics file.
    Facebook calendar can be downloaded only once a day. The date of the last
    download is saved in download_date.txt
    """
    # check if the download_date.txt file exists
    # if not, return an exception
    if not download_date_file_exists():
        raise exceptions.DownloadDateFileNotFoundException
    # check the last download date
    # if it is not written in download_date.txt or is not the same date as
    # today's, download the FB birthdays calendar
    # Otherwise, skip downloading
    with open(config.download_date, 'r+') as f:
        download_date = f.read()
        today = datetime.today().strftime('%Y-%m-%d')
        if not download_date or download_date != today:
            fb2cal.main2()
            f.seek(0)
            f.write(today)
            f.truncate()
            print("FB birthdays calendar is downloaded")
        else:
            print("FB birthdays calendar cannot be downloaded twice a day")


def _read_wishes(wish_type) -> List[str]:
    """"Reads in birthday wishes. If wish_type is 'funny', funny birthday
    wishes are read in, otherwise, serious birthday wishes are read in."""
    filename = config.funny_birthday_wish_path if wish_type == 'funny' else \
        config.serious_birthday_wish_path
    with open(filename, "r") as f:
        wishes = f.read().splitlines()
    return wishes


"""
Helper methods for filtering.
"""


def select_random_wish(wish_type) -> str:
    """Returns a random birthday wish."""
    wishes = _read_wishes(wish_type)
    return random.choice(wishes)



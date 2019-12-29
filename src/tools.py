from typing import List
from os import path
from settings import *
from fb_user import FBUser
import exceptions
import configparser
from ics import Calendar
from fb2cal.src import fb2cal


def account_details_file_exists() -> bool:
    """Check if account details file exists"""
    return path.exists(config.account_details_path)


def fb2cal_config_exists() -> bool:
    """Check if fb2cal config.ini file exists"""
    return path.exists(config.config_dir)


def ics_file_exists() -> bool:
    """Check if ics file exists"""
    return path.exists(config.calendar_dir)


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
    g = open(config.calendar_dir, 'rb')
    cal = Calendar(g.read().decode())
    for event in cal.events:
        event.description = None
    g.close()
    return cal


def set_up_fbuser() -> FBUser:
    """ (1) Read username and password from account_details
        (2) Copy account details to fb2cal config.ini
        (3) Parse a birthdays calendar from the ics file
        (4) Create and return an FB User
    """
    # check if account_details file exist
    # if exists, read account_details
    if account_details_file_exists():
        account_details = read_account_details()
    else:
        raise exceptions.AccountDetailsNotFoundException
    # check if fb2cal config.ini exists
    # if exists, set fb_email and fb_pass
    if fb2cal_config_exists():
        set_fb2cal_config_fb_email_fb_pass(account_details[0], account_details[1])
    else:
        raise exceptions.FB2CalConfigNotFoundException
    # check if ics file exists
    # if not, run fb2cal to create an ics file and download birthdays from FB
    # into the ics file
    if not ics_file_exists():
        fb2cal.main2()
    # parse a Calendar from the ics file
    cal = parse_ics()
    # create and return a new instance of FBUser
    user = FBUser(account_details[0], account_details[1], cal)
    return user

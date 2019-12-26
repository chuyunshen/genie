from ics import Calendar
import requests
from typing import List, Tuple

class AbstractCalendar:

    def __init__(self, calendar):
        self.events = self.parse_ics(calendar)

    def parse_ics(self, calendar_dir):
        pass


class BirthdayCalendar(AbstractCalendar):
    """ A calender consisting of all birthdays of a FBUser.
    events: a set of ics.Event. Important attributes of an Event include name,
    uid (facebook userid), begin (birthday, arrow format), and
    description(contains birthday message, str, initially set to None).
    """

    def parse_ics(self, calendar_dir):
        """ Parse a calendar from ics format"""
        g = open(calendar_dir, 'rb')
        cal = Calendar(g.read().decode())
        for event in cal.events:
            event.description = None
        g.close()
        return cal.events

    def get_calendar(self):
        """ Get/update birthday calendar from Facebook and saves the calendar at
        "fb2cal/src/calendar.ics".
        """
        fb2cal.main2()
        # dont do this too often or else the account will be banned

    def get_name_birthday_by_uid(self, uid):
        """ Returns the birthday of a specific userid, as an arrow object
        """
        for event in self.events:
            if event.uid == uid:
                name = event.name.split("'")[0]
                return name, event.begin


class HolidayCalendar(AbstractCalendar):
    """ A calendar consisting of holidays.
    Takes in a url of the icalendar to initialize.
    e.g.,
    "https://www.calendarlabs.com/ical-calendar/ics/39/Canada_Holidays.ics"

    events: a set of ics.Event. Important attributes of an Event include name
    (name of the holiday), begin (holiday date, arrow format),
    and description(contains a dictionary mapping uid to holiday message, initially set to an empty
    dictionary).
    """

    def parse_ics(self, calendar_url):
        """ Parse a calendar from ics format"""
        cal = Calendar(requests.get(calendar_url).text)
        for event in cal.events:
            event.description = {}
        return cal.events


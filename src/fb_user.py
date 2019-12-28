from datetime import datetime, timedelta

from arrow import Arrow
from fbchat import Client
from fbchat.models import *
from typing import Dict
from fb2cal.src import fb2cal
from ics import Calendar, Event
import os
from settings import *
from dateutil.relativedelta import relativedelta
from ics.grammar.parse import ContentLine


class FBUser:
    """
    Facebook user to login and congratulate her/his friends,
    having a birthday on the login date.
    """
    _username: str
    _password: str
    birthday_calendar: Calendar
    client: Client

    def __init__(self, username, password) -> None:
        """ Initialize a new Facebook user with the username and
        password stored in the account_details file.

        birthday_calendar: has attributes events (a set of ics.Event). Important
        attributes of an Event include name, uid (facebook user id),
        begin (birthday, arrow format), and description (contains birthday
        message, str).
        """
        self._username = username
        self._password = password
        self.client = _login(self)
        print("{} is logged in".format(self.client.uid))

        # if there does not exist a calendar, download from facebook, otherwise,
        # read in
        if not os.path.exists(config.calendar_dir):
            self.download_birthday_calendar()
        self.birthday_calendar = _parse_ics()

    def send_message(self, uid, message) -> None:
        """ Send a message"""
        self.client.send(Message(text=message),
                         thread_id=uid,
                         thread_type=ThreadType.USER)

    def send_scheduled_message(self, uid, message, today,
                               scheduled_date) -> None:
        """
        uid: str of Facebook user id
        message: str
        today: datetime.date object
        scheduled_date: arrow object
        """
        if today == scheduled_date.date():
            self.send_message(uid, message)
            print("Message to {} has been sent.".format(uid))

    def update_birthday_calendar(self) -> None:
        """ Updates the birthday calendar by checking for duplicated events and
        the adding the new events to the existing calendar. This method also
        deletes events for people who are not in the Facebook/Messenger
        friends list anymore.
        Regular updates of the birthday calendars ensures newly added friends'
        birthday information is added and if a friend's birthday this year
        (e.g., 2019-08-29) has passed, then that birthday event's begin
        attribute is updated to a new year's date (e.g., 2020-08-29), with the
        previously saved birthday message under attribute description removed
        (set to None).
        """
        self.download_birthday_calendar()
        new_cal = _parse_ics()
        all_old_uids = [event.uid for event in self.birthday_calendar.events]
        all_new_uids = [event.uid for event in new_cal.events]

        # events in the new calendar but not in the original calendar:
        for event in new_cal.events:
            if event.uid in all_old_uids:
                # if they have changed their birthdays or this year's birthday
                # has already passed--update to next year's
                updated_birthday = get_birthday_by_uid(event.uid, new_cal)
                if event.begin != updated_birthday:
                    event.begin = updated_birthday
            else:
                self.birthday_calendar.events.add(event)

        # events in the original calendar but not in the new calendar
        for event in self.birthday_calendar.events:
            if event.uid not in all_new_uids:
                # check if there is deleted friends and if they are still in
                # the friends list
                if event.uid not in self.get_friend_dict():
                    self.birthday_calendar.events.remove(event)

    def set_birthday_by_uid(self, uid, birthday) -> None:
        """Set the birthday for a friend by uid.
        Args:
            uid: str
            birthday: datetime
        """
        # Initialize birthday_event to a new event
        birthday_event = Event()
        # If the uid exists in the current birthday_calendar, we will delete
        # the old event.
        uid_exists = False
        for event in self.birthday_calendar.events:
            if event.uid == uid:
                birthday_event = event
                uid_exists = True
        if uid_exists:
            self.birthday_calendar.events.remove(birthday_event)
        birthday_event.uid = uid
        birthday_event.name = "{}'s Birthday".format(
            self.get_friend_dict()[uid][0])

        today = datetime.today()
        # Calculate the year as this year or next year based on if its past
        # current month or not
        # Also pad day, month with leading zeros to 2dp
        year = today.year if birthday.month >= today.month else (
                    today + relativedelta(years=1)).year
        month = '{:02d}'.format(birthday.month)
        day = '{:02d}'.format(birthday.day)
        birthday_event.begin = f'{year}-{month}-{day} 00:00:00'
        birthday_event.make_all_day()
        birthday_event.duration = timedelta(days=1)
        birthday_event.extra.append(
            ContentLine(name='RRULE', value='FREQ=YEARLY'))
        self.birthday_calendar.events.add(birthday_event)

    def save_calendar(self) -> None:
        """ Save the updated birthday calendar to calendar_dir.
        """
        with open(config.calendar_dir, 'w') as f:
            f.writelines(self.birthday_calendar)

    def get_uid_by_name(self, name) -> str:
        """ Finds a Facebook friend's uid by name. If the name does not exist
        in the friend list, NameError is raised.
        """
        friends = self.get_friend_dict()
        for uid in friends:
            if name == friends[uid][0]:
                return uid
        raise NameError

    def schedule_birthday_message_for_uid(self, uid, message) -> None:
        """Schedules a birthday message for Facebook friend with the given uid.
        """
        for event in self.birthday_calendar.events:
            if event.uid == uid:
                event.description = message
                return
        raise NameError

    def send_all_scheduled_birthday_messages(self, today) -> None:
        """Checks and sends all scheduled birthday messages."""
        for event in self.birthday_calendar.events:
            if event.description:
                self.send_scheduled_message(event.uid, event.description,
                                            today, event.begin)

    def get_friend_dict(self) -> Dict:
        """ Gets a dictionary of friends mapping from their uid to their name.
        """
        friend_dict = {}
        user_list = [user for user in self.client.get_contact_list() if
                     user.is_friend]

        for user in user_list:
            friend_dict[user.uid] = [user.name, user.url, user.photo]
        return friend_dict

    def download_birthday_calendar(self) -> None:
        """ Gets/updates birthday calendar from Facebook and saves the calendar at
        "fb2cal/src/calendar.ics".
        """
        fb2cal.main2()
        # dont do this too often or else the account will be banned


def _login(self) -> Client:
    """ Helper method to login to a Facebook account using a username and
    password from account_details"""
    return CustomClient(self._username, self._password)


def _parse_ics() -> Calendar:
    """ Parse a calendar from ics format"""
    g = open(config.calendar_dir, 'rb')
    cal = Calendar(g.read().decode())
    for event in cal.events:
        event.description = None
    g.close()
    return cal


def get_birthday_by_uid(uid, birthday_calendar) -> Arrow:
    """ Returns the birthday of a specific uid, as an arrow object
    """
    for event in birthday_calendar.events:
        if event.uid == uid:
            return event.begin


class CustomClient(Client):
    """CustomClient inherits from Client, to add on a method to get a list
    of Facebook/Messenger friends."""

    def get_contact_list(self):
        """Returns all contacts (friends or non-friends) of the client.

        Returns:
            list: :class:`User` objects

        Raises:
            FBchatException: If request failed
        """
        data = {"viewer": self._uid}
        j = self._payload_post("/chat/user_info_all", data)

        users = []
        for data in j.values():
            if data["type"] in ["user", "friend"]:
                users.append(User._from_all_fetch(data))
        return users
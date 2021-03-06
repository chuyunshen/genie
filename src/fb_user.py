from datetime import datetime, timedelta
from arrow import Arrow
from fbchat import Client
from fbchat.models import *
from typing import Dict, List
from ics import Calendar, Event
from settings import *
from dateutil.relativedelta import relativedelta
from ics.grammar.parse import ContentLine
import tools
import exceptions
from custom_client import CustomClient


class FBUser:
    """
    Facebook user to login and congratulate her/his friends,
    having a birthday on the login date.
    """
    _username: str
    _password: str
    birthday_calendar: Calendar
    client: CustomClient

    def __init__(self, username: str, password: str, cal: Calendar) -> None:
        """ Initialize a new Facebook user with the username and
        password stored in the account_details file.
        :param username: Facebook username
        :param password: Facebook password
        :param cal:      Has attributes events (a set of ics.Event). Important
                         attributes of an Event include name, uid (facebook
                         user id), begin (birthday, arrow format), and
                         description (contains birthday message, str).
        :return          None
        """
        self._username = username
        self._password = password
        self.birthday_calendar = cal
        self.client = _login(self)
        # save session cookies
        _save_session_cookies(self)

    def get_client(self) -> Client:
        """Return client object.
        :return Client object from the fbchat module
        """
        return self.client

    def get_name_by_uid(self, uid: str) -> str:
        """
        Find a FB friend with the provided uid and return her/his name
        If the uid is not found in the FB friends list, raise an exception
        :param uid:     uid to find
        :return:        friend's name associated with the uid
        """
        friends = self.get_friend_dict()
        if uid in friends:
            return friends[uid][0]
        else:
            raise exceptions.FriendNotFoundException

    def get_friend_dict(self) -> Dict:
        """ Gets a dictionary of friends mapping from their uid to their name.
        :return:    A dictionary mapping from uid to name, url, and photo url
        """
        friend_dict = {}
        user_list = [user for user in self.client.get_contact_list() if
                     user.is_friend]

        for user in user_list:
            friend_dict[user.uid] = [user.name, user.url, user.photo]
        return friend_dict

    def send_message(self, uid: str, message: str) -> None:
        """ Send a message.
        :param uid:     Message receiver's uid
        :param message: Message to send
        :return:        None
        """
        self.client.send(Message(text=message),
                         thread_id=uid,
                         thread_type=ThreadType.USER)

    def send_scheduled_message(self, event: Event) -> None:
        """ Send a scheduled birthday message and update the birthday's date
        to the next year's birthday.
        :param event:   Birthday event that contains information regarding uid
                        birthday, and message.
        :return:        None
        """
        self.send_message(event.uid, event.description)
        event.begin = event.begin.shift(years=1)
        print(f"Message to {event.uid} has been sent.")
        print(f"Birthday date is updated to {event.begin}.")

    def send_all_scheduled_birthday_messages(self, today: datetime) -> None:
        """Checks and sends all scheduled birthday messages.
        :param today:   today's date
        """
        for event in self.birthday_calendar.events:
            if event.description and today.date() == event.begin.date():
                self.send_scheduled_message(event)

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
        :return:    None
        """
        tools.download_birthday_calendar()
        new_cal = tools.parse_ics()
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

    def add_friend_birthday(self, uid: str, birthday_date: datetime) -> None:
        """
        Add a new friend and her/his birthday to the birthday calendar.
        :param uid:             Friend's FB UID
        :param birthday_date:   Friend's birthday date
        :return:                None
        """
        # find the friend's name per UID
        # if the UID is not in the FB friends list, return
        try:
            name = self.get_name_by_uid(uid)
        except exceptions.FriendNotFoundException:
            print(f"UID {uid} is not in your friends list.")
            return
        # create a birthday event
        new_birthday_event = \
            create_birthday_event(uid, name, birthday_date)
        # add a new event to the birthdays calendar
        self.birthday_calendar.events.add(new_birthday_event)

    def delete_birthday_by_uid(self, uid: str) -> None:
        """Delete a birthday event by uid."""
        uid_exists = False
        for event in self.birthday_calendar.events:
            if event.uid == uid:
                birthday_event = event
                uid_exists = True
        if uid_exists:
            self.birthday_calendar.events.remove(birthday_event)

    def save_calendar(self) -> None:
        """ Save the updated birthday calendar to calendar_dir.
        """
        with open(config.calendar_dir, 'w') as f:
            f.writelines(self.birthday_calendar)

    def schedule_birthday_message_for_uid(self, uid: str, message: str) -> None:
        """Schedules a birthday message for Facebook friend with the given uid.
        """
        for event in self.birthday_calendar.events:
            if event.uid == uid:
                event.description = message
                print("Message scheduled!")
                return
        raise NameError

    def logout(self) -> None:
        """ Logout from a Facebook account"""
        self.client.logout()
        print("User is logged out")


def _save_session_cookies(self) -> None:
    """
    Get session cookies and save them into cookies.txt
    :param self:    FBUser
    :return:        None
    """
    new_cookies = self.client.getSession()
    tools.save_cookies(new_cookies)


def _login(self) -> CustomClient:
    """ Helper method to login to a Facebook account using a username and
    password from account_details and, optionally, cookies.
    Save session cookies.
    If cookies.txt does not exit, raise exception."""
    if not tools.session_cookies_file_exists():
        raise exceptions.CookiesFileNotFoundException
    cookies = tools.read_cookies()
    if cookies:
        client = CustomClient(self._username, self._password, max_tries=1,
                              session_cookies=cookies)
        print("fbchat client logged in with cookies.")
    else:
        client = CustomClient(self._username, self._password, max_tries=1)
        print("fbchat client logged in without cookies.")
    return client


def get_birthday_by_uid(uid: str, birthday_calendar: Calendar) -> Arrow:
    """ Return the birthday of a specific uid, as an arrow object
    :param uid:                   uid to get birthday for
    :param birthday_calendar:     birthday calendar within which to search for
                                  uid
    :return                       Arrow object representing the birthday
    """
    for event in birthday_calendar.events:
        if event.uid == uid:
            return event.begin


def create_birthday_event(uid: str, name: str,
                          birthday_date: datetime) -> Event:
    """ Create a birthday event with the provided parameters.
    :param uid:             Friend's FB UID
    :param name:            Friend's FB name
    :param birthday_date:   Friend's birthday date
    :return:                Birthday event
    """
    # Initialize birthday_event to a new event
    birthday_event = Event()
    birthday_event.uid = uid
    birthday_event.name = f"{name}'s Birthday"
    today = datetime.today()
    # Calculate the year as this year or next year based on if its past
    # current month or not
    year = today.year if birthday_date.month >= today.month else (
            today + relativedelta(years=1)).year
    # Pad day, month with leading zeros to 2dp
    month = '{:02d}'.format(birthday_date.month)
    day = '{:02d}'.format(birthday_date.day)
    birthday_event.begin = f'{year}-{month}-{day} 00:00:00'
    birthday_event.make_all_day()
    birthday_event.duration = timedelta(days=1)
    birthday_event.extra.append(
        ContentLine(name='RRULE', value='FREQ=YEARLY'))
    return birthday_event


def get_uid_by_name(name: str, friends: dict) -> List[str]:
    """ Finds a Facebook friend's uid by name from a friend dictionary.
    If the name does not exist in the friend list, NameError is raised.
    Returns a list of uids.
    :param name:       Name to find uid for
    :param friends:    A dictionary mapping from uid to name, url, and photo url
    :return:           A list of uids
    """
    uids = [uid for uid in friends if friends[uid][0] == name]
    if uids:
        return list(uids)
    raise NameError


def set_up_fbuser() -> FBUser:
    """Helper method for creating and returning class instances.
        (1) Read username and password from account_details
        (2) Copy account details to fb2cal config.ini
        (3) Parse a birthdays calendar from the ics file
        (4) Create and return an FB User
        :return: FBUser
    """
    # check if account_details file exist
    # if exists, read account_details
    if tools.account_details_file_exists():
        account_details = tools.read_account_details()
    else:
        raise exceptions.AccountDetailsNotFoundException
    # check if fb2cal config.ini exists
    # if exists, set fb_email and fb_pass
    if tools.fb2cal_config_exists():
        tools.set_fb2cal_config_fb_email_fb_pass(account_details[0],
                                                 account_details[1])
    else:
        raise exceptions.FB2CalConfigNotFoundException
    # check if ics file exists
    # if not, run fb2cal to create an ics file and download birthdays from FB
    # into the ics file
    if not tools.ics_file_exists():
        tools.download_birthday_calendar()
    # parse a Calendar from the ics file
    cal = tools.parse_ics()
    # create and return a new instance of FBUser
    user = FBUser(account_details[0], account_details[1], cal)
    # update birthday calendar
    user.update_birthday_calendar()
    return user


def save_cal_and_logout(fb_user: FBUser):
    """
    (1) Send birthday messages scheduled for today
    (2) Save calendar to the .ics file
    (3) Logout from fbchat
    """
    today = datetime.today()
    # Send scheduled birthday messages
    fb_user.send_all_scheduled_birthday_messages(today)
    # Save calendar to the .ics file
    fb_user.save_calendar()
    # Logout from fbchat
    fb_user.logout()
    print("Logged out")

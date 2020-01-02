from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError
from datetime import datetime
from prompt_toolkit.document import Document
from fb_user import *


class DateValidator(Validator):
    """DateValidator inherits from Validator and is used for validating dates.
    """

    def validate(self, document: Document) -> None:
        """Validates dates.
        :param document: Document to validate
        :returns: None
        :raises ValidationError: If document.text is not a valid date
        """
        try:
            datetime.strptime(document.text, '%m-%d')
        except ValueError:
            raise ValidationError(
                message="Please enter a valid date in the format of mm-dd.",
                cursor_position=len(document.text))  # Move cursor to end


class StringValidator(Validator):
    """StringValidator inherits from Validator and is used for validating
    strings.
    """

    def validate(self, document) -> None:
        """Validate strings.
        :param document: Document to validate
        :returns: None
        :raises ValidationError: If document.text is an empty string
        """
        if not document.text or document.text.strip() == '':
            raise ValidationError(
                message="Please enter a non-empty input.",
                cursor_position=len(document.text))  # Move cursor to end


def validate_name(name, friends: dict) -> None:
    """Validate names.
    :param name:             Name to validate
    :param friends:          A dictionary of friends mapping from uid to name,
                             url, and photo url.
    :returns:                None
    :raises ValidationError: If name does not exist in friends or is an empty
    string
    """
    try:
        get_uid_by_name(name, friends)
    except NameError:
        raise ValidationError(
            message="You don't have a friend with this name",
            cursor_position=len(name))  # Move cursor to end
    if not name or name.strip() == '':
        raise ValidationError(
            message="Please enter a non-empty input.",
            cursor_position=len(name))  # Move cursor to end


class Menu:
    """
    This class contains attributes and methods related to displaying a menu
    for the command line interface.
    """
    main_menu_question = [
        {
            'type': 'list',
            'name': 'main_menu',
            'message': 'What would you like to do?',
            'choices': ["Edit a friend's birthday",
                        "Schedule/Update a Facebook birthday message",
                        "Exit"],
        }]

    friend_birthday_question = [
        {
            'type': 'input',
            'name': 'friend_birthday',
            'message': "Please enter your friend's birthday, "
                       "in the format of mm-dd",
            'validate': DateValidator,
        }]

    birthday_message_type_question = [
        {
            'type': 'list',
            'name': 'birthday_message_type',
            'message': 'How would you like to generate the birthday message?',
            'choices': ["1) Generate a random birthday message",
                        "2) Draft a birthday message"],
        }]

    random_birthday_message_type_question = [
        {
            'type': 'list',
            'name': 'random_birthday_message_type',
            'message': 'Would you like your message to be serious or funny?',
            'choices': ["Serious",
                        "Funny"],
            'filter': lambda val: val.lower()
        }]

    draft_birthday_message_question = [
        {
            'type': 'input',
            'name': 'drafted_birthday_message',
            'message': 'Please draft your birthday message:',
            'validate': StringValidator,
        }]

    style = style_from_dict({
        Token.QuestionMark: '#E91E63 bold',
        Token.Selected: '#b16286 bold',
        Token.Instruction: '',  # default
        Token.Answer: '#83a598 bold',
        Token.Question: '',
    })

    def __init__(self, friends: dict) -> None:
        """Initialize a menu.
        :param friends:     A dictionary of friends mapping from uid to name,
                            url, and photo url.
        """

        print("Welcome to Genie!")
        self.friends = friends
        self.friend_selection_question = [
            {
                'type': 'list',
                'name': 'friend_selection',
                'message': 'There are multiple friends with the same name. '
                           'Their Facebook profile pictures are included in '
                           'the links.',
                'choices': self.friends  # might not work, need an array
            }]

        self.friend_name_question = [
            {
                'type': 'input',
                'name': 'friend_name',
                'message': "Please enter your friend's first and last name "
                           "(e.g., Jane Doe)",
                'validate': lambda text: validate_name(text, self.friends)
            }]

    def update_friends(self, friends: dict) -> None:
        """Update friends.
        :param friends:     A dictionary of friends mapping from uid to name,
                            url, and photo url.
        :return:            None
        """
        self.friends = friends

    def get_main_menu_choice(self) -> str:
        """
        Print main menu choices and get user's response.
        :return:    User's main menu choice
        """
        answer = prompt(self.main_menu_question, style=self.style)['main_menu']
        if answer == self.main_menu_question[0]['choices'][0]:
            return "edit"
        elif answer == self.main_menu_question[0]['choices'][1]:
            return "schedule"
        else:
            return "exit"

    def get_friend_name(self) -> str:
        """Print the friend name question and get user's response.
        :return:    User's friend name
        """
        return prompt(self.friend_name_question,
                      style=self.style)['friend_name']

    def get_friend_selection(self) -> str:
        """Print a list of friend with the same name to select from and get
        user's response.
        :return:    User's friend name
        """
        return prompt(self.friend_selection_question,
                      style=self.style)['friend_selection']

    def get_friend_uid(self, fb_user: FBUser) -> str:
        """
        Get an FB friend's name from the user input,
        search for this friend's UID among user's FB friends
        and, if found, return her/his uid.
        Otherwise, print out "Friend not found".
        :param fb_user:     FB user to provide a friend's name
        :return:            FB frind's UID
        """
        try:
            friend_name = self.get_friend_name()
            friend_uids = get_uid_by_name(friend_name,
                                          fb_user.get_friend_dict())
            if len(friend_uids) > 1:
                return self.get_friend_selection()
            else:
                return friend_uids[0]
        except NameError:
            print(f"Friend not found.")

    def get_friend_birthday(self) -> str:
        """Print the friend birthday question and get user's response.
        :return:    User's friend birthday
        """
        return prompt(self.friend_birthday_question,
                      style=self.style)['friend_birthday']

    def get_birthday_message_type(self) -> str:
        """Print the birthday message type question and get user's response.
        :return:    User's preferred birthday message type
        """
        answer = prompt(self.birthday_message_type_question,
                        style=self.style)['birthday_message_type']
        if answer == self.birthday_message_type_question[0]['choices'][0]:
            return "random"
        else:
            return "drafted"

    def get_random_birthday_message_type(self) -> str:
        """Print the random birthday message type question and get user's
        response.
        :return:    User's preferred random birthday message type
        """
        return prompt(self.random_birthday_message_type_question,
                      style=self.style)['random_birthday_message_type']

    def get_drafted_birthday_message(self) -> str:
        """Print the drafted birthday message question and get user's response.
        :return:    User's drafted birthday message
        """
        return prompt(self.draft_birthday_message_question,
                      style=self.style)['drafted_birthday_message']

    def get_birthday_message(self) -> str:
        """
        Get a user's drafted message or a random template message,
        depending on the user's input choice.
        :return:    birthday message - drafted or random template
        """
        birthday_message_type = self.get_birthday_message_type()
        if birthday_message_type == 'random':
            random_birthday_message_type = \
                self.get_random_birthday_message_type()
            return tools.select_random_wish(random_birthday_message_type)
        else:
            return self.get_drafted_birthday_message()

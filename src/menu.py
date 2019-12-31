from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError
import datetime
# from fb_user import get_uid_by_name
from fb_user import *


class DateValidator(Validator):
    def validate(self, document):
        try:
            datetime.datetime.strptime(document.text, '%m-%d')
        except ValueError:
            raise ValidationError(
                message="Please enter a valid date in the format of mm-dd.",
                cursor_position=len(document.text))  # Move cursor to end


class StringValidator(Validator):
    def validate(self, document):
        if not document.text or document.text.strip() == '':
            raise ValidationError(
                message="Please enter a non-empty input.",
                cursor_position=len(document.text))  # Move cursor to end


def validate_name(name, friend_list):
    try:
        get_uid_by_name(name, friend_list)
    except NameError:
        raise ValidationError(
            message="You don't have a friend with this name",
            cursor_position=len(name))  # Move cursor to end
    if not name or name.strip() == '':
        raise ValidationError(
            message="Please enter a non-empty input.",
            cursor_position=len(name))  # Move cursor to end


class Menu:
    main_menu_question = [
        {
            'type': 'list',
            'name': 'main_menu',
            'message': 'What would you like to do?',
            'choices': ["Edit a friend's birthday",
                        "Schedule/Update a Facebook birthday message"],
        }]

    friend_birthday_question = [
        {
            'type': 'input',
            'name': 'friend_birthday',
            'message': 'Please enter your friend\'s birthday, '
                       'in the format of mm-dd',
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

    def __init__(self, friend_list):
        print("Welcome to Genie--your one-stop program for automated birthday"
              "wishes.")
        self.friend_list = friend_list
        self.friend_selection_question = [
            {
                'type': 'list',
                'name': 'friend_selection',
                'message': 'There are multiple friends with the same name. '
                           'Their Facebook profile pictures are included in '
                           'the links.',
                'choices': self.friend_list
            }]

        self.friend_name_question = [
            {
                'type': 'input',
                'name': 'friend_name',
                'message': "Please enter your friend's first and last name "
                           "(e.g., Jane Doe)",
                'validate': lambda text: validate_name(text, self.friend_list)
            }]

    def update_friend_list(self, friend_list):
        self.friend_list = friend_list

    def get_main_menu_choice(self):
        answer = prompt(self.main_menu_question, style=self.style)['main_menu']
        if answer == self.main_menu_question[0]['choices'][0]:
            return "edit"
        else:
            return "schedule"

    def get_friend_name(self):
        return prompt(self.friend_name_question,
                      style=self.style)['friend_name']

    def get_friend_selection(self):
        return prompt(self.friend_selection_question,
                      style=self.style)['friend_selection']

    def get_friend_birthday(self):
        return prompt(self.friend_birthday_question,
                      style=self.style)['friend_birthday']

    def get_birthday_message_type(self):
        answer = prompt(self.birthday_message_type_question,
                        style=self.style)['birthday_message_type']
        if answer == self.birthday_message_type_question[0]['choices'][0]:
            return "random"
        else:
            return "drafted"

    def get_random_birthday_message_type(self):
        return prompt(self.random_birthday_message_type_question,
                      style=self.style)['random_birthday_message_type']

    def get_drafted_birthday_message(self):
        return prompt(self.draft_birthday_message_question,
                      style=self.style)['drafted_birthday_message']

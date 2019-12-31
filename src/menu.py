from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError
import datetime

style = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#b16286 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#83a598 bold',
    Token.Question: '',
})


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


friends_list = ['1', '2']  # somehow pass it into here.
print('Welcome to Genie!')

main_menu_question = [
    {
        'type': 'list',
        'name': 'main_menu',
        'message': 'What would you like to do?',
        'choices': ["1) Edit a friend's birthday",
                    "2) Schedule/Update a Facebook birthday message"],
        'filter': lambda val: val[0]
    }]

friend_name_question = [
    {
        'type': 'input',
        'name': 'friend_name',
        'message': 'Please enter your friend\'s first and last name (e.g., '
                   'Jane Doe)',
        'validate': StringValidator
    }]

friend_selection_question = [
    {
        'type': 'list',
        'name': 'friend_selection',
        'message': 'There are multiple friends with the same name. '
                   'Their Facebook profile pictures are included in the links.',
        'choices': friends_list
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
        'choices': ["Generate a random birthday message",
                    "Draft a birthday message"],
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


def menu():
    main_menu_choice = prompt(main_menu_question, style=style)
    friend_name = prompt(friend_name_question, style=style)
    friend_selection = prompt(friend_selection_question, style=style)
    friend_birthday = prompt(friend_birthday_question, style=style)
    birthday_message_type = prompt(birthday_message_type_question, style=style)
    random_birthday_message_type = prompt(random_birthday_message_type_question,
                                          style=style)
    drafted_birthday_message = prompt(draft_birthday_message_question,
                                      style=style)

<p align="center">
  
<img src="https://imgur.com/ErP9Ujr.png[/img]" alt="Genie Logo" height="72">
  
</p>

<h3 align="center">Genie</h3>

<p align="center">
Why remember birthdays when Genie can grant wishes to all your Facebook friends?  <br>
  </p>
  
Genie logs users in onto Facebook and fetches birthday information. Users can
draft or select random birthday wish messages that will be automatically sent on
friends' birthdays.

Genie is built on [Python](https://www.tensorflow.org/api_docs/python).

For our next steps, we would like to integrate holidays, be cross-platform, and 
move Genie online.

## Table of contents

- [Quick Start](#quick-start)
- [Demonstration](#demonstration)
- [What's included](#whats-included)
- [Documentation](#documentation)
- [Tests](#tests)
- [Questions and contributions](#questions-and-contributions)
- [Thanks](#thanks)
- [Copyright and license](#copyright-and-license)

## Quick start

* Make sure you have `virtualenv` installed (usually installed by `pip3 install virtualenv`)
* Clone the repository
* Create a virtualenv in the project directory
```
$ virtualenv env -p `which python3`
```
* Activate the virtualenv from the project dir for working in terminal
```
$ source env/bin/activate
```
(Also, setup the the project interpreter in PyCharm)

* Install the project requirements by running
```
$ pip3 install -r requirements.txt
```

* Create a file `account_details.txt` under `config` directory. 
This file should have two lines: Facebook username and Facebook password.

* Create a file `download_date.txt` under `config` directory. 
Leave this file empty.

* Create a file `cookies.txt` under `config` directory. 
Leave this file empty.

## How to Run
```
$ cd genie
$ export PYTHONPATH='.'
$ python3 src/main.py
```
## Demonstration
<img src="https://imgur.com/6EaItVN.gif[/img]" alt="Main menu options" height="60">
<br />
<img src="https://imgur.com/GREH8Aw.gif[/img]" alt="Draft a birthday message" height="50">

## Note 
Our current version requires users to run the program every day to ensure
the messages are delivered.

If you are using a relatively new account, please visit the mobile site of 
Facebook (m.facebook.com) to skip all the new-account welcome/set-up. Otherwise,
the program may not be able to continue.

## Documentation

## Tests
To run tests:

## What's included
```
genie
├── LICENSE
├── README.md
├── config
│   └── test
├── docs
│   ├── funny_birthday_wish_template.txt
│   ├── main_menu.gif
│   └── serious_birthday_wish_template.txt
├── fb2cal
│   ├── LICENSE
│   ├── README.md
│   ├── config
│   │   └── config.ini
│   ├── requirements.txt
│   └── src
│       ├── __init__.py
│       ├── _version.py
│       └── fb2cal.py
├── requirements.txt
└── src
    ├── config.py
    ├── custom_client.py
    ├── exceptions.py
    ├── fb_user.py
    ├── main.py
    ├── menu.py
    ├── settings.py
    ├── test
    │   ├── __init__.py
    │   ├── config_test.py
    │   └── test_fbuser.py
    └── tools.py
```
## Thanks
We thank Daniel Moran for reviewing our code and our Facebook bot Boris Petrov 
for tirelessly testing the program.

## Questions and Contributions 
Feel free to open an issue and/or make a pull request.

## Copyright and License
Genie is released under the [MIT License](https://opensource.org/licenses/MIT).

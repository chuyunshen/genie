<p align="center">
  
<img src="https://imgur.com/ErP9Ujr.png[/img]" alt="Genie Logo" height="72">
  
</p>

<h3 align="center">Genie</h3>

<p align="center">
Why remember birthdays when Genie can grant wishes to all your Facebook friends?  <br>
  </p>

## Quick start

* Make sure you have `virtualenv` installed (usually installed by `pip3 install virtualenv`)
* Clone the repository
* Create a virtualenv in the project directory
```
virtualenv env -p `which python3`
```
* Activate the virtualenv from the project dir for working in terminal
```
source env/bin/activate
```
(Also, setup the the project interpreter in PyCharm)

* Install the project requirements by running
```
pip install -r requirements.txt
```

* Create a file `account_details.txt` under `docs` directory. 
This file should have two lines: Facebook username and Facebook password.

## What's included
```
genie
├── README.md
├── config
│   └── test
├── docs
│   ├── funny_birthday_wish_template.txt
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
    ├── exceptions.py
    ├── fb_user.py
    ├── main.py
    ├── settings.py
    ├── test
    │   ├── __init__.py
    │   ├── config_test.py
    │   └── test_fbuser.py
    ├── tools.py
    └── wish_generator.py
```

# Local development environment

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
## [Centralized Student Notification System]()

This is a centralized
notification web app developed using Flask, bootstrap and python 3.

See  the live version on [https://aidns.herokuapp.com/](https://aidns.herokuapp.com/).

## Features

* User account management
* Account personalization
* Instant email notifications

## Running the project
* Create virtualenv.
    `virtualenv -p python3 venv`
* Navigate to the app directory
    `cd aidns`
* Activate virtualenv
    `source venv/bin/activate`
* Install the dependencies
    `pip install requirements.txt`

Now, ideally, this application should run fine by starting the server
by using `python manage.py runserver`. But if you run after following steps, you'll get a database error from SQLAlchemy.
`sqlalchemy.exc.OperationalError`

* The database is not actually in working condition, so for that to work, you'll need to create a new context for the app to run in.

Open a new terminal and go through the following steps.

* `python3`
* 'from app import create_app'
* `from app.models import * #  imports all the tables`
* `app = create_app('default')`
* `app.app_context().push()  # creates a new context for running the app in terminal`
* `create_db() # creates the empty database using models.py`
* `Role.insert_roles() # insert data into the created roles table`

Finally, run the server.

* `python manage.py runserver`

The server will probably run at `http://127.0.0.1:5000/`.

## Development
* Used [pep8 coding guidelines](https://www.python.org/dev/peps/pep-0008/)
* Used sublime text editor.
* Hosted on Heroku.
* Developed using Python, Bootstrap and Flask.

## Contributors       
* [Vishal Kumar Gupta](https://github.com/variable17)
* [Utkarsh Bhatt](https://github.com/utkarshbhatt12)

## LICENCE
MIT License

Copyright (c) 2017 Vishal Kumar Gupta and Utkarsh Bhatt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

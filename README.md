# ASA VPN Dashboard
This is an app that utilizes the Cisco ASA REST APIs to display the results of ASA CLI commands onto a web dashboard. The information from multiple firewalls can be viewed on this dashboard. The data needed to use the APIs is saved into a MongoDB database. 

## Overview
This repository contains a Python Flask app that uses the Cisco ASA REST API to send the CLI commands `show version`, `show vpn-sessiondb detail anyconnect`, and `show vpn load-balancing` and then displays the formatted results of the commands on the dashboard. 

## Contacts
* Danielle Stacy (dastacy)

## Solution Components
* Cisco ASA
* Cisco AnyConnect
* Cisco ASA REST API
* Flask
* SQLAlchemy
* Python 3.9

##Prerequisites
- **ASA Setup**:
  - **Enable REST API on ASA**: To install and enable the REST API Agent on an ASA, follow [these steps](https://www.cisco.com/c/en/us/td/docs/security/asa/api/qsg-asa-api.html#56532).
  - **ASA Credentials**: To use the APIs, it is necessary to know the IP addresses, usernames, and passwords of the ASAs you want to add to the dashboard. Make note of these credentials.
- **SQL Database Setup**:
  - **Set Secret Key**: Set a secret key of your choice in __init__.py on line 11:
  ```python
    app.config['SECRET_KEY'] = 'ENTER SECRET KEY HERE'
    ```

## Installation/Configuration
1. Clone this repository with `git clone https://github.com/gve-sw/gve_devnet_asa_vpn_dashboard` and open the directory of the root repository.
2. Create a Python virtual environment and activate it (find instructions to do that [here](https://docs.python.org/3/tutorial/venv.html).
3. Install the requirements with pip3 install -r requirements.txt
4. Set up the SQLite database with Flask SQLAlchemy. Open the Python Interactive Console by typing `python3` in the terminal. The primary prompt for the next command should be three greater-than signs (>>>). From here, type the following commands:
```
>>> from flask_app import sql_db, create_app, models
>>> sql_db.create_all(app=create_app())
```
5. Set your flask environment variables. The flask app is located in the directory `flask_app`, and the app should be run in the development environment until production ready. To do this, type this in the terminal:
```
$ export FLASK_APP=flask_app
$ export FLASK_ENV=development
```

## Usage
To launch the app, run the command `flask run`

Access the dashboard on your preferred web browser at the IP address for your local host: `http://127.0.0.1:5000`.

This should take you to a login page. If no users have been registered, click to register a user on the side panel. Otherwise, login with a previously created user.

Once logged in, you will be taken to a home screen that displays information about each firewall that has been added to the database. If no firewalls have been added yet, then the home screen will be mostly empty other than the sidebar. The sidebar has options to add a firewall, remove a firewall, view load balacing information about the firewalls, and logout. If firewalls have been added to the database, then there should be a button on the tile with the information about that firewall labeled `Show VPN Clients`. Clicking this button will open a new webpage that displays information about the VPN users associated with that firewall.

# Screenshots

![/IMAGES/0image.png](/IMAGES/0image.png)

![/IMAGES/ASAVPNDashboardWorkflow.png](/IMAGES/ASAVPNDashboardWorkflow.png)

Register User and Login Screens

![/IMAGES/register_screen.png](/IMAGES/register_screen.png)
![/IMAGES/login_screen.png](/IMAGES/login_screen.png)

Home page

![/IMAGES/home_screen.png](/IMAGES/home_screen.png)

Add and delete firewalls

![/IMAGES/add_screen.png](/IMAGES/add_screen.png)
![/IMAGES/delete_screen.png](/IMAGES/delete_screen.png)

Show load balancing page

![/IMAGES/load_balancing_screen.png](/IMAGES/load_balancing_screen.png)

Show VPN clients page

![/IMAGES/vpn_clients_screen.png](/IMAGES/vpn_clients_screen.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.

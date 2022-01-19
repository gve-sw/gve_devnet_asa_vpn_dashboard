#!/usr/bin/env python3
'''
Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
'''
from flask import Flask, render_template, redirect, request, url_for, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user
from . import sql_db
from .db import *
from .asav import *
from .vpnClient import VPN_Client
from .models import Firewall


main = Blueprint('main', __name__)

'''this function extracts the software version, serial number, license mode,
hardware model, uptime, and the name of the output from the show version
command on the ASA'''
def parseShowVer(output, asa_username, asa_password, asa_host):
    version_info_list = output[0].strip().splitlines() #make a list with each item being each line of the output

    #then search each line of the list for the keywords to pull the information from that line
    for line in version_info_list:
        if "Software Version" in line:
            software_version = line
            break

    for line in version_info_list:
        if "Serial Number" in line:
            parsed_line = line.split(": ")
            serial = parsed_line[-1]
            break

    for line in version_info_list:
        if "License mode" in line:
            parsed_line = line.split(": ")
            license_mode = parsed_line[-1]
            break

    for line in version_info_list:
        if "Hardware" in line:
            parsed_line = line.split(": ")
            model = parsed_line[-1]
            break

    for line in version_info_list:
        if " up " in line:
            parsed_line = line.split("up")
            uptime = parsed_line[-1]
            asa_name = parsed_line[0]
            break

    #create a dictionary with the information found from this function as well as the username, password, and ip address
    data = {
        "username": asa_username,
        "password": asa_password,
        "model": model,
        "name": asa_name,
        "ip": asa_host,
        "uptime": uptime,
        "serial": serial,
        "software_version": software_version,
        "license_mode": license_mode
    }

    return data


'''this function extracts the usaernames, login duration, inactivity time,
operating system of the client, AnyConnect version used by the client, and the
number of bytes transmitted by the client from the output of the show vpn
clients command on the ASA'''
def parseShowVPNClients(vpn_client):
    clients = []

    os_flag = True
    vers_flag = True
    tx_flag = True

    #check each line of the output for the following keywords - here we will find the desired information
    for line in vpn_client:
        if "Username" in line:
            parsed_line = line.split(": ")
            user_text = parsed_line[1]
            parsed_user = user_text.split(" ")
            user = parsed_user[0]

            new_client = VPN_Client(user) #VPN_Client is a class with member variables for all the information pulled from the VPN Clients
            clients.append(new_client)
            #the output is divided by client, so we create these flags to keep track of where we are while parsing the output
            os_flag = True
            vers_flag = True
            tx_flag = True

        if "Duration" in line:
            parsed_line = line.split(": ")
            login_duration = parsed_line[-1]
            new_client.login_duration = login_duration

        if "Inactivity" in line:
            parsed_line = line.split(": ")
            inactivity = parsed_line[-1]
            new_client.inactivity = inactivity

        if "Client OS" in line and os_flag:
            parsed_line = line.split(": ")
            client_os = parsed_line[-1].strip()
            new_client.os = client_os
            os_flag = False

        if "Client Ver" in line and vers_flag:
            parsed_line = line.split(": ")
            client_version = parsed_line[-1].strip()
            new_client.version = client_version
            vers_flag = False

        if "Bytes Tx" in line and tx_flag:
            parsed_line = line.split(": ")
            client_tx = parsed_line[-1].strip()
            new_client.tx = client_tx
            tx_flag = False

    return clients


'''this function extracts the information from Show Load Balancing CLI command
output to more easily display it in a table format'''
def parseShowLoadBalancing(load_balancing_info):
    #this output is divided into three different sections, so these flags are used to keep track of where we are in the output while parsing it
    status_section = False
    license_section = False
    inactive_section = False

    load_balancing_info = load_balancing_info["response"][0].strip().splitlines() #make a list with each item being a line of the output
    load_balancing_txt = []
    fw_load_balance = {}

    #loop through the output, adding each line that isn't a line of dashes or an empty line to a new list
    for line in load_balancing_info:
        if "---" not in line and line != "":
            load_balancing_txt.append(line)

    #loop through this new list without the dashes and empty lines and search for the keywords
    for line in load_balancing_txt:
        if status_section:
            status_info = line.split()
            status = status_info[0]
            role = status_info[1]
            cluster_ip = status_info[-1]

            fw_load_balance['status'] = status
            fw_load_balance['role'] = role
            fw_load_balance['cluster_ip'] = cluster_ip

            status_section = False
        elif license_section:
            if "AnyConnect" not in line and "Limit" not in line:
                load_info = line.split()
                anyconnect_load = load_info[2]
                other_load = load_info[5]

                fw_load_balance['anyconnect_load'] = anyconnect_load
                fw_load_balance['other_load'] = other_load

                license_section = False
        elif inactive_section:
            if "Inactive" not in line:
                inactive_info = line.split()
                inactive_load = inactive_info[1]

                fw_load_balance['inactive_load'] = inactive_load

                inactive_section = False

        if "Status" in line:
            status_section = True
        elif "Total License Load:" in line:
            license_section = True
        elif "Inactive" in line:
            inactive_section = True

    return fw_load_balance


#this function creates our home page - it will display the firewalls and the information from the show version commands
@main.route('/', methods=('GET', 'POST'))
@login_required
def home():
    #if a post method is used on this page, the Show VPN Clients button was clicked, so we should open a new page displaying the VPN client information
    if request.method == 'POST':
        if request.form.get('firewall') != '':
            firewall = request.form.get('firewall')
            if request.form.get('function') == 'VPN Clients':
                return redirect(url_for('main.vpnClients', id=firewall))

    fws = Firewall.query.all()
    firewalls = []
    for fw in fws:
        asav = ASAVcontroller(fw.ip, fw.username, fw.password)
        version_info = asav.showVersion()

        data = parseShowVer(version_info, fw.username, fw.password, fw.ip)
        data['id'] = fw.id

        firewalls.append(data)

    return render_template("home.html", firewalls=firewalls)


#this function creates our add firewall page which can be accessed from the sidebar
@main.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    #if a post method is being used on this page, the Add firewall button was clicked, so we need to add a new firewall to the database
    if request.method == 'POST':
        if request.form.get("asa_host") != "":
            asa_host = request.form.get("asa_host")

        if request.form.get("asa_username") != "":
            asa_username = request.form.get("asa_username")

        if request.form.get("asa_password") != "":
            asa_password = request.form.get("asa_password")

        asav = ASAVcontroller(asa_host, asa_username, asa_password)
        new_asa = Firewall(asa_username, asa_password, asa_host)
        sql_db.session.add(new_asa)
        sql_db.session.commit()

        return redirect(url_for('main.home'))

    return render_template("add.html")


#this function creates our delete firewall page that can be accessed from the sidebar
@main.route('/delete', methods=('GET', 'POST'))
@login_required
def delete():
    firewalls = Firewall.query.all() #retrieve all the firewalls from the database to create our list

    #if a post method is being used on this page, the delete firewall button was clicked, so we need to remove the specified firewall(s) from the database
    if request.method == 'POST':
        firewalls_selected = request.form.getlist('asa')
        for firewall in firewalls_selected:
            delete_firewall = Firewall.query.filter_by(id=firewall).one()
            sql_db.session.delete(delete_firewall)
            sql_db.session.commit()

        return redirect(url_for('main.home'))

    return render_template('delete.html', firewalls=firewalls)


#this function creates our show load balancing page that can be accessed from the sidebar
@main.route('/loadBalancing', methods=('GET',))
@login_required
def loadBalancing():
    fws = Firewall.query.all() #retrieve all firewalls from the database

    load_balancing = []

    for fw in fws:
        asav = ASAVcontroller(fw.ip, fw.username, fw.password)
        load_balancing_info = asav.showLoadBalancing() #run the show load balancing command on the firewall
        fw_load_balance = parseShowLoadBalancing(load_balancing_info) #parse output to display on page
        fw_load_balance['ip'] = fw.ip
        load_balancing.append(fw_load_balance)

    return render_template("loadBalancing.html", info=load_balancing)


#this function creates our show vpn clinets page that can be accessed from the button on the individual firewall tile
@main.route('/vpnClients/<id>', methods=('GET',))
@login_required
def vpnClients(id):
    fw = Firewall.query.filter_by(id=id).one() #get the firewall represented by the tile from the database

    asav = ASAVcontroller(fw.ip, fw.username, fw.password)
    vpn_client_info = asav.showVPNDetail() #run show vpn command on the firewall
    vpn_client = vpn_client_info[0].strip().splitlines() #create list from with each item being a line from the output

    clients = parseShowVPNClients(vpn_client) #parse the output in list form to display on page

    for client in clients:
        client.printout() #validate parsing function

    return render_template("vpnClients.html", clients=clients)

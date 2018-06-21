# coding: utf-8

import poplib
import string, random
import StringIO, rfc822
import logging
import MySQLdb
import sys
import getpass
import csv
from datetime import datetime
from dateutil.parser import parse



def revisar(x):
    for item in x:
        id, size = string.split(item)
        resp, text, octets = server.retr(id)
        text = string.join(text, "\n")
        file = StringIO.StringIO(text)
        message = rfc822.Message(file)
        body = message.fp.read()
        sender = message['From']
        subject = message['Subject']
        date = message['Date']
        dt = str(parse(date))
        dd = dt.split()
        if 'DevOps' in message['Subject'] or 'DevOps' in body:
            com.execute("INSERT IGNORE INTO Senders(sen_name) VALUES('" + sender + "');")
            conexion.commit()
            com.execute("INSERT INTO Subjects(sub_text, date, sen_id) VALUES('" + subject + "', '" + dd[0] + "', (SELECT sen_id from Senders WHERE sen_name='" + sender + "'));")
            conexion.commit()

def leer(x):
    global h
    global u
    global d
    with open(x, "r") as archivo:
        reader = csv.reader(archivo, delimiter=" ")
        for linea in reader:
            if linea[0] == "HOST":
                h = linea[2]
            elif linea[0] == "USER":
                u = linea[2]
            elif linea[0] == "DB":
                d = linea [2] 

SERVER = "pop.gmail.com"
USER  = raw_input("Ingrese su email: ")
PASSWORD = getpass.getpass("Ingrese su contraseña: ")

try:
    logging.debug('connecting to ' + SERVER)
    server = poplib.POP3_SSL(SERVER)
    logging.debug('logging in')
    server.user(USER)
    server.pass_(PASSWORD)
    logging.debug('listing emails')
    resp, items, octets = server.list()
except poplib.error_proto:
    sys.exit("Usuario y/o contraseña incorrectos")

leer("connection.txt")
conexion = MySQLdb.connect(host = h, user = u)
com = conexion.cursor()
com.execute("SHOW DATABASES LIKE '" + d + "'")
x = com.rowcount
if x == 0:
    com.execute("CREATE DATABASE IF NOT EXISTS " + d)
    com.execute("USE " + d)
    com.execute("CREATE TABLE IF NOT EXISTS Senders(sen_id INT AUTO_INCREMENT, sen_name CHAR(50) UNIQUE, PRIMARY KEY (sen_id));")
    com.execute("CREATE TABLE IF NOT EXISTS Subjects(sub_id INT AUTO_INCREMENT, sub_text CHAR(100), date DATE, sen_id INT, PRIMARY KEY (sub_id), FOREIGN KEY (sen_id) REFERENCES Senders(sen_id));")
    conexion.close()
    conexion = MySQLdb.connect(host = h, user = u, db = d) 
    com = conexion.cursor()
    revisar(items)
    conexion.close()
    print("Se ha creado la base '" + d + "' con los mails encontrados")
else:
    conexion.close()
    conexion = MySQLdb.connect(host = h, user = u, db = d) 
    com = conexion.cursor()
    revisar(items)
    conexion.close()
    print("Se agregaron registros a la base con los mails encontrados")

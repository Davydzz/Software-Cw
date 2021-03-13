from user import User
from dbConnection import DBConnection
import pytest
import argparse
from csv import reader
import base64
import os
import hashlib


db = DBConnection()


def main():
    with open('MOCK_DATA.csv', 'r') as read_obj:
    # pass the file object to reader() to get the reader object
        csv_reader = reader(read_obj)

    testUsers(csv_reader)


def test_connection():
    # assume rethinkdb is running, otherwise connection will fail
    with db.createConnection("database.db") as conn:
        assert conn.is_open() == True


def testUsers(userRows):
    header = next(userRows)

    if header != None:
        for elem in userRows:
            salt = str(base64.b64encode(os.urandom(16)),"utf-8")
            toHash = salt + elem[3] #take the hash of this todo
            hashedPassword = hashlib.sha256(bytes(toHash,"utf-8")).hexdigest()

            assert db.addUser(salt, hashedPassword, elem[0], elem[1], elem[2]) == True


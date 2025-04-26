import time

import pytest
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash


PASSWORD = 'newpassword1'
TEST_USER = {'username': 'newuser1',
              'password': PASSWORD,
              'password_hash': lambda hash: check_password_hash(hash, PASSWORD),  # salted
              'account_created_time': None}


class TestUserRecord():

    def insert_user_raw_sql(self, username, password, mock_db):
        account_created_time = time.time()
        insertion_query = text(
            f'INSERT INTO users (username, password_hash, account_created_time) '
            f'VALUES ("{username}", "{generate_password_hash(password)}", {account_created_time});')
        with mock_db.engine.connect() as con:
            con.execute(insertion_query)
            con.commit()

    def remove_user_raw_sql(self, username, mock_db):
        query = text(f'DELETE FROM users WHERE username="{username}"')
        with mock_db.engine.connect() as con:
            con.execute(query)
            con.commit()

    def select_user_raw_sql(self, username, mock_db):
        query = text(f'SELECT * FROM users WHERE username="{username}"')
        with mock_db.engine.connect() as con:
            result = con.execute(query)
        return result.first()[0]

    def test_create_user_success(self, mock_db):
        """ verify that db code creates a user with the expected attributes """
        assertions = []  # TODO soft & hard assertions
        mock_db.create_user(TEST_USER['username'], TEST_USER['password'])
        for k, v in TEST_USER.items():
            if k not in ['account_created_time', 'password']:
                expected = v
                observed = self.select_user_raw_sql(TEST_USER["username"], mock_db)
                print(f'expecting\n{expected}\nfound\n{observed}')
                if k == 'password_hash':
                    assertions.append(
                    (v(observed), f'check db hash of password {TEST_USER["password"]}'))
                else:
                    assertions.append((
                        observed == expected, f'expected user attr {expected}, found {observed}'))
        for assertion in assertions:
            assert assertion

    def test_create_user_failure(self, mock_db):
        """
        create a user, then use db code to try to create a duplicate user and verify failure
        """
        self.insert_user_raw_sql(
            TEST_USER['username'],
            TEST_USER['password'],
            mock_db)
        assert self.select_user_raw_sql(TEST_USER['username'], mock_db) is not None,\
            f'test setup: successfully inserted user {TEST_USER["username"]}'
        result = mock_db.create_user(TEST_USER['username'], TEST_USER['password'])
        assert result == False, f'db code should fail to create duplicate user {TEST_USER["username"]}'
        # TODO bad passwords? Other reasons?

    def test_delete_user_success(self, mock_db):
        """
        insert a user, then use db code to delete it and verify that it was deleted
        """
        self.insert_user_raw_sql(
            TEST_USER['username'],
            TEST_USER['password'],
            mock_db)
        mock_db.delete_user(TEST_USER['username'])
        query = text(
            f'SELECT username FROM users WHERE username="{TEST_USER["username"]}";')
        with mock_db.engine.connect() as con:
            result = con.execute(query).first()
        assert result is None

    def test_delete_user_failure(self, mock_db):
        """ use db code to delete a user that doesn't exist and verify that it failed """
        result = mock_db.delete_user(TEST_USER['username'])
        assert result == False
        # other cases?

    def test_login_success(self, mock_db):
        """ verify that db code can verify a user's password when it's correct """
        self.insert_user_raw_sql(
            TEST_USER['username'],
            TEST_USER['password'],
            mock_db)
        assert self.select_user_raw_sql(TEST_USER['username'], mock_db) is not None,\
            f'test setup: successfully inserted user {TEST_USER["username"]}'
        result = mock_db.login(TEST_USER['username'], TEST_USER['password'])
        assert result == True, f'db code verified correct password for {TEST_USER["username"]}'


    def test_login_failure(self, mock_db):
        """
        verify that db code does not verify a user when the given password is incorrect,
        as well as when an invalid username is given
        """
        self.insert_user_raw_sql(
            TEST_USER['username'],
            TEST_USER['password'],
            mock_db)
        assert self.select_user_raw_sql(TEST_USER['username'], mock_db) is not None,\
            f'test setup: successfully inserted user {TEST_USER["username"]}'
        result = mock_db.login(TEST_USER['username'], 'thisisnottehcorrectpassword')
        assert result == False, f'db code rejected incorrect password for {TEST_USER["username"]}'
        # TODO should these be separate test functions?
        result = mock_db.login('userthatdoesnotexist', 'thisisnottehcorrectpassword')
        assert result == False, f'db code rejected invalid username'

from data_model import Database


class TestInsertIntoDatabase():
    db = Database()
    def test_insert_into_database(self):
        """
        Inserts a test item into the database, queries the database to confirm the new item,
        removes the item.

        Runs against whatever the ANSIFIER_DATABASE env var is set to
        TODO centralize name of this var, assess better ways of configuring which backend
        """

        with open('./tests/static/test_ansify_url_expected.txt', 'r') as rf:
            ansi_art = rf.read()

        uid = self.db.insert_art(ansi_art, 'ansi-escaped')

        print(f'inserted art {uid} into db {self.db}')

        art_retrieved = self.db.retrieve_art(uid)

        print(f'retrieved art w/ len {len(art_retrieved)} from db {self.db}')

        assert ansi_art == art_retrieved

        print(f'validated equality of art in db')

        self.db.delete_art(uid)

        print(f'deleted art with uid {uid} from db {self.db}')

from bson.objectid import ObjectId
import run as app
import unittest


class TestRun(unittest.TestCase):
    """ 
    run application tests
    """
    
    def test_check_connection(self):
        """ test connection to the database """
        self.assertIsNotNone(app.check_connection())
    
    def test_get_users_count(self):
        """ test the user count in the database """
        self.assertFalse(app.get_users_count() == 0)


    def test_get_user_info(self):
        """ test for getting the user's full name, vocab_count and userId  """
        
        name = app.get_user_info("skullphish", name=True)
        vocab_count = app.get_user_info("skullphish", vocab_count=True)
        userId = app.get_user_info("skullphish", userId=True)
        
        self.assertTrue(name == "damian rodbari")
        self.assertEqual(vocab_count,0)
        self.assertTrue(userId ==  ObjectId("5bb8a0c006f1f8105bc3bb23"))

    
    def test_create_user(self):
        """ test for duplicate user prevention  """
        
        new_user = {"username": "beny1976", "vocab_count": 0, "name": "beny rood", "sex": "male", "dob": "18/10/1979"}
        msg = app.create_user(predefined_user=new_user)
        self.assertTrue(msg != "")
    
    
    
    
if __name__ == "__main__":
    unittest.main()
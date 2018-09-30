from bson.objectid import ObjectId
import run as app
import unittest


class testRun(unittest.TestCase):
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
        """ test for getting the user's full name, setup_count and userId  """
        
        name = app.get_user_info("skullphish", name=True)
        setup_count = app.get_user_info("skullphish", setup_count=True)
        userId = app.get_user_info("skullphish", userId=True)
        
        self.assertTrue(name == "damian rodbari")
        self.assertEqual(setup_count,0)
        self.assertTrue(userId ==  ObjectId("5bb02b0e1572a1581e73fbda"))

    
    def test_create_user(self):
        """ test for duplicate user prevention  """
        
        new_user = {"username": "beny1976", "setup_count": 0, "name": "beny rood" }
        msg = app.create_user(predefined_user=new_user)
        self.assertTrue(msg != "")
    
    
    
    
    if __name__ == "__main__":
        unittest.main()
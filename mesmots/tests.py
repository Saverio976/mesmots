import unittest
from mots import Mots

class TestStringMethods(unittest.TestCase):

    def test_read_data(self):
        mots = Mots()

    def test_search(self):
        mots = Mots()
        r1 = mots.endswith(mots.tail(mots.split("saisissant")[0], 2))
        res = mots.apply(r1)
        self.assertEqual(len(res), 2)

if __name__ == "__main__":
    print("import OK")
    print("Starting unittest")
    unittest.main()
    print("Ending unittest")

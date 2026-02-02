import unittest
from mots import Mots

class TestMethods(unittest.IsolatedAsyncioTestCase):

    async def test_read_data(self):
        mots = Mots()

    async def test_search(self):
        mots = Mots()
        r1 = mots.endswith(mots.tail((await mots.split("saisissant"))[0], 2))
        res = await mots.apply(r1)
        print("1", res)
        self.assertTrue(isinstance(res, list))
        self.assertNotEqual(len(res), 0)

    async def test_split(self):
        mots = Mots()
        res = await mots.syllab_tokenize.tokenize("macron")
        print("2", res)
        self.assertTrue(isinstance(res, list))
        assert isinstance(res, list)
        self.assertNotEqual(len(res), 0)
        
        res = await mots.syllab_decoder.get(orthosyll="bon", ortho_before="", ortho_after="jour")
        print("3", res)
        self.assertTrue(isinstance(res, list))
        self.assertNotEqual(len(res), 0)
        
        res = await mots.split("bonjour")
        print("4", res)
        self.assertTrue(isinstance(res, list))
        self.assertNotEqual(len(res), 0)
        

if __name__ == "__main__":
    print("import OK")
    print("Starting unittest")
    unittest.main()
    print("Ending unittest")

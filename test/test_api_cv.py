import unittest

from api_service.app import create_app
from test.test_api_base import AbstractTest


class MyTestCase(unittest.TestCase, AbstractTest):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = create_app(config="TESTING").test_client()
        cls.clear_collection()

    def setUp(self) -> None:
        MyTestCase.clear_collection()
        MyTestCase.clear_collection(entrypoint="/ctrl_voc/")


    # ------------------------------------------------------------------------------------------------------------------
    # GET

    def test_get_property_no_param(self):
        """ Get list of properties without query parameter"""
        MyTestCase.insert_two(self.app)

        res = self.app.get("/ctrl_voc/", follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json), 1)

    def test_get_cv_deprecate_param(self):
        """ Get list of properties with query parameter deprecate """
        MyTestCase.insert_two(self.app)

        for deprecated in [True, False]:
            res = self.app.get(f"/ctrl_voc?deprecated={deprecated}", follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            if deprecated:
                self.assertEqual(len(res.json), 2)
            else:
                self.assertEqual(len(res.json), 1)

    # ------------------------------------------------------------------------------------------------------------------
    # POST

    def test_insert_cv_minimal(self):
        """ Add minimal controlled vocabulary """

        data = {"label": "Test CV",
                "name": "Test CV",
                "description": "Test CV",
                "items": [{"label": "Test item 1", "name": "Test item 1"}]}

        res = AbstractTest.insert(MyTestCase.app, data, entrypoint="/ctrl_voc/")

        self.assertEqual(res.status_code, 201)
        self.assertTrue(all([key in res.json.keys() for key in ["message", "id"]]))

    def test_insert_cv_full(self):
        """ Add a controlled vocabulary containing a description and a synonyms """

        data = {"label": "Test CV",
                "name": "Test CV",
                "description": "Test CV",
                "items": [{"label": "Test item 1",
                           "name": "Test item 1",
                           "description": "Simple description",
                           "synonyms": ["A test", "This is a test label"]
                           }]
                }

        res = AbstractTest.insert(MyTestCase.app, data, entrypoint="/ctrl_voc/")

        self.assertEqual(res.status_code, 201)
        self.assertTrue(all([key in res.json.keys() for key in ["message", "id"]]))

    # ------------------------------------------------------------------------------------------------------------------
    # DELETE

    def test_deprecate(self):
        self.test_insert_cv_minimal()

        results = MyTestCase.get_ids(MyTestCase.app, entrypoint="/ctrl_voc/")

        for entry in results.json:
            MyTestCase.app.delete(f"/ctrl_voc/id/{entry['id']}")

        results = MyTestCase.get(MyTestCase.app, entrypoint="/ctrl_voc", params={"deprecated": True})

        for entry in results.json:
            self.assertTrue(entry['deprecated'])




        pass

    # ------------------------------------------------------------------------------------------------------------------
    # Helper methods

    @staticmethod
    def insert_two(app):
        data1 = {"label": "Test CV 1",
                 "name": "Test CV 1",
                 "description": "Test CV 1",
                 "items": [{"label": "Test item 1", "name": "Test item 1"}],
                 "deprecated": False}

        data2 = {"label": "Test CV 2",
                 "name": "Test CV 2",
                 "description": "Test CV 2",
                 "items": [{"label": "Test item 1", "name": "Test item 1"}],
                 "deprecated": True}

        for data in [data1, data2]:
            res = AbstractTest.insert(MyTestCase.app, data=data, entrypoint="/ctrl_voc/")

if __name__ == '__main__':
    unittest.main()

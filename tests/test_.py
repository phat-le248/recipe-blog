from unittest import TestCase

# from ..app import create_app


class Test(TestCase):
    def setUp(self):
        # For context required tests
        # app = create_app("testing")
        # self.app_ctx = app.app_context()
        # self.app_ctx.push()
        pass

    def tearDown(self):
        # For context required tests
        # self.app_ctx.pop()
        pass

    def test_example(self):
        self.assertTrue(True)

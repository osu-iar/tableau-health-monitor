import unittest
from main import setup_parser


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = setup_parser()

    def test_default_health(self):
        args = self.parser.parse_args([])

        self.assertEqual(args.command, 'health')

    def test_explicit_health(self):
        args = self.parser.parse_args(['health'])

        self.assertEqual(args.command, 'health')

    def test_license(self):
        args = self.parser.parse_args(['license'])

        self.assertEqual(args.command, 'license')

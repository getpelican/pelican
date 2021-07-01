from unittest.mock import Mock

from pelican.tests.support import unittest


class Test_abbr_role(unittest.TestCase):
    def call_it(self, text):
        from pelican.rstdirectives import abbr_role

        rawtext = text
        lineno = 42
        inliner = Mock(name="inliner")
        nodes, system_messages = abbr_role("abbr", rawtext, text, lineno, inliner)
        self.assertEqual(system_messages, [])
        self.assertEqual(len(nodes), 1)
        return nodes[0]

    def test(self):
        node = self.call_it("Abbr (Abbreviation)")
        self.assertEqual(node.astext(), "Abbr")
        self.assertEqual(node["explanation"], "Abbreviation")

    def test_newlines_in_explanation(self):
        node = self.call_it("CUL (See you\nlater)")
        self.assertEqual(node.astext(), "CUL")
        self.assertEqual(node["explanation"], "See you\nlater")

    def test_newlines_in_abbr(self):
        node = self.call_it("US of\nA \n (USA)")
        self.assertEqual(node.astext(), "US of\nA")
        self.assertEqual(node["explanation"], "USA")

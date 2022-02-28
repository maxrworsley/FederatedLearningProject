import _pickle
import unittest

import MessageDefinitions as md
from Serialisation import Serialiser as s


class TestStandardMessage(unittest.TestCase):
    def test_serialisation_no_errors(self):
        pre_base_message = md.BaseMessage()
        serialised_message = s.serialise_message(pre_base_message)
        self.assertGreater(len(serialised_message), 6)

    def test_deserialisation(self):
        pre_message = md.BaseMessage()
        post_message = s.deserialise_message(s.serialise_message(pre_message))

        self.assertEqual(pre_message.__repr__(), post_message.__repr__())

    def test_deserialisation_error(self):
        serialised_message = s.serialise_message(md.BaseMessage())
        serialised_message[8] = 30

        with self.assertRaises(ValueError):
            s.deserialise_message(serialised_message)


if __name__ == '__main__':
    unittest.main()

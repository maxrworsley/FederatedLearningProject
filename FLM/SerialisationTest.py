import _pickle
import unittest
from Serialisation import Serialiser as s
import MessageDefinitions as md


class TestStandardMessage(unittest.TestCase):
    def test_serialisation_no_errors(self):
        pre_base_message = md.BaseMessage(1, 0, 2, 123456789)
        serialised_message = s.serialise_message(pre_base_message)
        self.assertGreater(len(serialised_message), 6)

    def test_deserialisation(self):
        pre_message = md.BaseMessage(1, 0, 2, 123456789)
        post_message = s.deserialise_message(s.serialise_message(pre_message))

        self.assertEqual(pre_message.__repr__(), post_message.__repr__())

    def test_deserialisation_error(self):
        serialised_message = s.serialise_message(md.BaseMessage(1, 0, 2, 123456789))
        serialised_message[8] = 30

        with self.assertRaises(_pickle.UnpicklingError):
            deserialised_message = s.deserialise_message(serialised_message)


if __name__ == '__main__':
    unittest.main()

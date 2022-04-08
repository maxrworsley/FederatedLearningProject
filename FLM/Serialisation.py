import pickle


class Serialiser:
    """Wraps serialisation for messages to go over the wire"""
    API_VERSION = 1
    BYTES_HEADER = 2
    BYTES_API_VERSION = 2
    BYTES_MESSAGE_ID = 2

    @staticmethod
    def serialise_message(message_object):
        """
        Take a message and convert it to binary for the wire
        :param message_object: Message to be serialised
        :return: Binary conmbination of header and payload with message in
        """
        api_version = Serialiser.API_VERSION.to_bytes(Serialiser.BYTES_API_VERSION, byteorder='big')
        message_id = message_object.id.to_bytes(Serialiser.BYTES_MESSAGE_ID, byteorder='big')
        header = bytearray(api_version + message_id)
        header_length = len(header).to_bytes(Serialiser.BYTES_HEADER, byteorder='big')

        payload = pickle.dumps(message_object)

        message = bytearray(header_length + header + payload)
        return message

    @staticmethod
    def deserialise_message(message):
        """
        Take binary representation of message and convert to message object
        :param message: Binary of message
        :return: Unspecified message object
        """
        if len(message) <= 0:
            raise ValueError('Tried to deserialise empty message')
        elif len(message) <= (Serialiser.BYTES_MESSAGE_ID + Serialiser.BYTES_HEADER + Serialiser.BYTES_API_VERSION):
            raise ValueError('Tried to deserialise message with too short a header')

        header_length = int.from_bytes(message[:2], byteorder='big')
        header = bytearray(message[2:2 + header_length])
        api_version = int.from_bytes(header[:Serialiser.BYTES_API_VERSION], byteorder='big')
        message_id = int.from_bytes(header[Serialiser.BYTES_API_VERSION:], byteorder='big')

        if api_version != Serialiser.API_VERSION:
            print(
                f"Possible message API mismatch. Current version {Serialiser.API_VERSION}, received message on {api_version}")
            raise ValueError('Possibly received message from wrong API version.')

        try:
            message_object = pickle.loads(message[2 + header_length:])
        except pickle.UnpicklingError:
            raise ValueError('Could not deserialise')

        return message_object

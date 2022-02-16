class BaseMessage:
    id = 1
    round_id = -1
    sender_id = -1
    receiver_id = -1
    time_sent = 0

    def __init__(self, round_id, sender_id, receiver_id, time_sent):
        self.round_id = round_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.time_sent = time_sent

    def __str__(self):
        return (f"""
        sender_id={self.sender_id},
        receiver_id={self.receiver_id},
        time_sent={self.time_sent},
        message_id={self.id}
        """)

    def __repr__(self):
        return f'{self.id}{self.round_id}{self.sender_id}{self.receiver_id}{self.time_sent}'


class StopSession(BaseMessage):
    id = 2


class CheckConnection(BaseMessage):
    id = 3


class CheckConnectionResponse(BaseMessage):
    id = 4


class RequestJoinRound(BaseMessage):
    id = 5


class ResponseJoinRound(BaseMessage):
    id = 6
    accepted_into_round = False
    heartbeat_interval = 5


class ClientHeartbeat(BaseMessage):
    id = 7


class RequestTrainModel(BaseMessage):
    id = 8
    checkpoint_bytes = ""


class ResponseTrainModel(BaseMessage):
    id = 9
    checkpoint_bytes = ""


class RequestLeaveRound(BaseMessage):
    id = 10
    reason_for_leaving = "Cancelled"


class RoundCancelled(BaseMessage):
    id = 11

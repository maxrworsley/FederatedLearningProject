from FLM import MessageDefinitions
import NodeWrapper
import time


class ClientManager:
    nodes = []
    keep_gathering_nodes = True
    local_socket = None

    def __init__(self, local_socket):
        self.local_socket = local_socket

    def gather_nodes(self, target_number):
        current_count = 0

        while current_count < target_number and self.keep_gathering_nodes:
            new_node = NodeWrapper.NodeWrapper(self.local_socket)
            new_node.start()
            print("Waiting for node to send message")
            join_round_request = new_node.receive(self.keep_gathering_nodes)

            if self.keep_gathering_nodes:
                print("Node added")
                new_node.active = True
                new_node.sender_id = 0
                new_node.receiver_id = current_count + 1
                new_node.send(MessageDefinitions.ResponseJoinRound())
                self.nodes.append(new_node)
                current_count += 1
            else:
                print("Node not added, as node gather has stopped")

        self.update_active()

    def update_active(self):
        self.send_to_all(MessageDefinitions.CheckConnection())
        self.receive_from_all(MessageDefinitions.CheckConnectionResponse())

    def send_model_to_nodes(self, model_message):
        self.send_to_all(MessageDefinitions.CheckConnection())
        self.receive_from_all(MessageDefinitions.RequestTrainModel.id)
        self.send_to_all(model_message)

    def wait_for_node_models(self):
        # todo not receiving model. Node is being marked as inactive
        return self.receive_from_all(MessageDefinitions.ResponseTrainModel.id, timeout=90)

    def send_to_all(self, message):
        for node in self.nodes:
            if node.active:
                node.send(message)

    def receive_from_all(self, target_id, timeout=5):
        responses = [None] * len(self.nodes)

        within_timeout = True
        start_time = time.time()

        while not all(responses) and within_timeout:
            for i in range(len(self.nodes)):
                if not responses[i]:
                    response = self.nodes[i].receive(block=False)
                    if response:
                        if response.id == target_id:
                            responses[i] = response

            time_now = time.time()
            if time_now - start_time > timeout:
                print("Timeout")
                within_timeout = False

        for i in range(len(self.nodes)):
            if not responses[i] and self.nodes[i].active:
                self.nodes[i].active = False
                print(f"Lost node due to inactivity. Node id was {self.nodes[i].receiver_id}")

        return responses

    def __del__(self):
        print("Stopping nodes")
        for node in self.nodes:
            node.stop()
        print("Connection to all nodes terminated")
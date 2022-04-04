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
            join_round_request = new_node.receive(self.keep_gathering_nodes)

            if not join_round_request:
                continue

            if self.keep_gathering_nodes:
                new_node.active = True
                new_node.sender_id = 0
                new_node.receiver_id = current_count + 1
                new_node.send(MessageDefinitions.ResponseJoinRound())
                self.nodes.append(new_node)
                current_count += 1

    def update_active(self):
        self.send_to_all(MessageDefinitions.CheckConnection())
        self.receive_from_all(MessageDefinitions.CheckConnectionResponse())

    def are_any_active(self):
        for node in self.nodes:
            if node.active:
                return True
        return False

    def send_model_to_nodes(self, model_message):
        self.send_to_all(model_message)

    def wait_for_node_models(self):
        # todo could make timeout configurable

        return self.receive_from_all(MessageDefinitions.ResponseTrainModel.id, timeout=30)

    def send_to_all(self, message):
        for node in self.nodes:
            if node.active:
                node.send(message)

    def receive_from_all(self, target_id, timeout=5):
        responses = [None] * len(self.nodes)

        start_time = time.time()

        while not all(responses):
            time.sleep(0.5)
            for i in range(len(self.nodes)):
                if not responses[i]:
                    response = self.nodes[i].receive(block=False)
                    if response:
                        if response.id == target_id:
                            responses[i] = response

            time_elapsed = time.time() - start_time
            if time_elapsed > timeout:
                print(f"Timeout while waiting for target message {target_id}.")
                break

        for i in range(len(self.nodes)):
            if not responses[i] and self.nodes[i].active:
                self.nodes[i].active = False
                print(f"Lost node due to inactivity. Node id was {self.nodes[i].receiver_id}")

        return responses

    def stop_prematurely(self):
        for node in self.nodes:
            node.stop_premature()
            print("Connection to all nodes terminated")

    def __del__(self):
        print("Stopping nodes")
        for node in self.nodes:
            node.stop()
        print("Connection to all nodes terminated")

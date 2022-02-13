class Coordinator:
    tf_handler = None

    def set_handler(self, handler):
        self.tf_handler = handler

    def start_round(self):
        print("Starting round")
        self.tf_handler.get_data()

        self.tf_handler.create_model()
        self.tf_handler.fit_model(50)

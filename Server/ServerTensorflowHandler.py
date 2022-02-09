class TensorflowHandler:
    training_data = None
    training_labels = None
    test_data = None
    test_labels = None

    def __init__(self, name, datawrapper):
        self.name = name
        self.data_wrapper = datawrapper
        print(f'Tensorflow handler created.')

    def get_data(self):
        dataset = self.data_wrapper.get_data()
        self.training_data = dataset.sample(frac=0.8, random_state=0)
        self.test_data = dataset.drop(self.training_data.index)
        print(self.training_data)

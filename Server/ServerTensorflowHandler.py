import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt


class TensorflowHandler:
    training_features = None
    training_labels = None
    test_features = None
    test_labels = None
    linear_model = None

    def __init__(self, name, datawrapper):
        self.name = name
        self.data_wrapper = datawrapper
        print(f'Tensorflow handler created.')

    @staticmethod
    def plot_loss(history):
        plt.plot(history.history['loss'], label='loss')
        plt.plot(history.history['val_loss'], label='val_loss')
        plt.xlabel('Epoch')
        plt.ylabel('Error [target]')
        plt.legend()
        plt.grid(True)

    def get_data(self):
        dataset = self.data_wrapper.get_data()
        training_data = dataset.sample(frac=0.8, random_state=0)
        test_data = dataset.drop(training_data.index)

        self.training_features = training_data.copy()
        self.test_features = test_data.copy()
        self.training_labels = self.training_features.pop('target')
        self.test_labels = self.test_features.pop('target')

    def create_model(self):
        normalizer = tf.keras.layers.Normalization(axis=-1)

        normalizer.adapt(np.array(self.training_features))

        self.linear_model = tf.keras.Sequential([
            normalizer,
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(units=1)
        ])

        self.linear_model.compile(
            optimizer=tf.optimizers.Adam(learning_rate=0.05),
            loss='mean_absolute_error'
        )

    def fit_model(self, epochs):
        test_results_before = self.linear_model.evaluate(
            self.test_features,
            self.test_labels,
            verbose=0
        )

        history = self.linear_model.fit(
            self.training_features,
            self.training_labels,
            epochs=epochs,
            verbose=0,
            validation_split=0.2
        )

        test_results_after = self.linear_model.evaluate(
            self.test_features,
            self.test_labels,
            verbose=0
        )

        self.plot_loss(history)
        plt.show()

        print(f'Test results before = {test_results_before}, and after = {test_results_after}')

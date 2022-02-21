import tensorflow as tf
import numpy as np


class ModelTrainer:
    training_features = None
    training_labels = None
    test_features = None
    test_labels = None
    model = None
    history = []

    def __init__(self, datawrapper):
        self.data_wrapper = datawrapper

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

        self.model = tf.keras.Sequential([
            normalizer,
            tf.keras.layers.Dense(64, activation='sigmoid'),
            tf.keras.layers.Dense(64, activation='sigmoid'),
            tf.keras.layers.Dense(units=1)
        ])

        self.model.compile(
            optimizer=tf.optimizers.Adam(learning_rate=0.05),
            loss='mean_absolute_error'
        )

    def fit_model(self, epochs, plot_history=False):
        pre_loss = self.model.evaluate(
            self.test_features,
            self.test_labels,
            verbose=0
        )
        print(f"Model before training has loss {pre_loss}")

        history = self.model.fit(
            self.training_features,
            self.training_labels,
            epochs=epochs,
            verbose=0,
            validation_split=0.2
        )
        post_loss = self.model.evaluate(
            self.test_features,
            self.test_labels,
            verbose=0
        )
        print(f"Post loss = {post_loss}")

        self.history.append(history)

        if plot_history:
            print("Would print history if matplotlib was installed")
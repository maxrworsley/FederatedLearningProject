import tensorflow as tf


class StopTrainingCallback(tf.keras.callbacks.Callback):
    keep_training = True

    def on_epoch_end(self, epoch, logs=None):
        if not self.keep_training:
            self.model.stop_training = True


class ModelTrainer:
    training_features = None
    training_labels = None
    test_features = None
    test_labels = None
    model = None
    history = []
    keep_training = True

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
        self.model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(9,)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(units=1)
        ])

        self.model.compile(
            optimizer=tf.optimizers.Adam(learning_rate=0.05),
            loss='mean_absolute_error'
        )

    def load_model(self, path):
        self.model = tf.keras.models.load_model(path + '/model')

    def fit_model(self, epochs, validation_split, stopping_callback):
        self.train(epochs, validation_split, stopping_callback)

    def train(self, epochs, split, stop_callback):
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
            validation_split=split,
            callbacks=[stop_callback]
        )

        post_loss = self.model.evaluate(
            self.test_features,
            self.test_labels,
            verbose=0
        )
        print(f"Post loss = {post_loss}")

        self.history.append(history)

    def save_model(self, path):
        tf.keras.models.save_model(self.model, path)

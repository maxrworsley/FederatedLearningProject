import tensorflow as tf


class TensorflowHandler:
    model = None

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

    def save_current_model(self, working_directory):
        path = working_directory + "/model"
        tf.keras.models.save_model(self.model, path)

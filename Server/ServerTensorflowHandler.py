import logging
import os

import tensorflow as tf


class TensorflowHandler:
    """Handles creation/loading of model for nodes to use"""
    model = None

    def get_model(self, load_path=None):
        if load_path:
            try:
                self.model = tf.keras.models.load_model(load_path)
                logging.info("Loaded saved model")
                return
            except IOError:
                logging.warning("Tried to load saved model, but couldn't be found")
            except ImportError:
                logging.warning("Tried to load saved model, but hdf5 file is not present")

        logging.info("Creating model")

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

    def set_model(self, model):
        self.model = model

    def save_current_model(self, working_directory):
        path = os.path.join(working_directory, "model")
        tf.keras.models.save_model(self.model, path)

    @staticmethod
    def load_model(path):
        return tf.keras.models.load_model(path)

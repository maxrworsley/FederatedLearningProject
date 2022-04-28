import matplotlib.pyplot as plt


class Visualiser:
    """Handles graphing of node results"""
    @staticmethod
    def plot_history_over_epochs(history_with_info, epochs):
        plt.style.use('ggplot')
        for history, ID, location in history_with_info:
            plt.figure(figsize=(5, 5))
            loss = history.history['loss']
            val_loss = history.history['val_loss']
            epochs_range = range(epochs)

            plt.plot(epochs_range, loss, label='Training Data Loss')
            plt.plot(epochs_range, val_loss, label='Validation Data Loss')

            plt.xlabel("Epoch")
            plt.ylabel("Mean absolute loss")
            plt.ylim([0, 0.3])

            plt.legend(loc='upper right')
            plt.title(f'Loss for node ID {ID} ({location})')

            plt.show()

    @staticmethod
    def plot_loss_same_graph(history_with_info, epochs):
        plt.style.use('ggplot')
        plt.figure(figsize=(5, 5))

        for history, ID, location in history_with_info:
            plt.plot(range(epochs), history.history['val_loss'], label=f'Loss for ID {ID} ({location})')

        plt.xlabel("Epoch")
        plt.ylabel("Mean absolute loss")
        plt.ylim([0, 0.3])

        plt.legend(loc='upper right')
        plt.title("Evaluation loss ")

        plt.show()

    @staticmethod
    def plot_evaluation_losses(history_with_info):
        plt.style.use('ggplot')
        plt.figure(figsize=(5, 5))

        val_losses = []
        ids = []
        # Get the last evaluation result
        for history, ID, location in history_with_info:
            val_losses.append(history.history['val_loss'][-1])
            ids.append(f"{ID} ({location})")

        x_names = [i for i, _ in enumerate(ids)]
        plt.bar(x_names, val_losses)
        plt.xlabel("Node ID")
        plt.ylabel("Validation loss")
        plt.title("Losses for each ID")
        plt.xticks(x_names, ids)
        plt.show()

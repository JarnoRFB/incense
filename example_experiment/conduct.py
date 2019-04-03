# -*- coding: future_fstrings -*-
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import pandas as pd
from matplotlib.animation import FFMpegWriter
from tensorflow.python.keras.callbacks import Callback
from sacred import Experiment
from sacred.observers import MongoObserver
from sacred.utils import apply_backspaces_and_linefeeds


class MetricsLogger(Callback):
    """Callback to log loss and accuracy to sacred database."""

    def __init__(self, run):
        super().__init__()
        self._run = run

    def on_epoch_end(self, epoch, logs):
        self._run.log_scalar("training_loss", float(logs["loss"]), step=epoch)
        self._run.log_scalar("training_acc", float(logs["acc"]), step=epoch)


def plot_confusion_matrix(confusion_matrix, class_names, figsize=(15, 12), fontsize=14):
    """Prints a confusion matrix, as returned by sklearn.metrics.confusion_matrix, as a heatmap.

    Based on https://gist.github.com/shaypal5/94c53d765083101efc0240d776a23823

    Arguments
    ---------
    confusion_matrix: numpy.ndarray
        The numpy.ndarray object returned from a call to sklearn.metrics.confusion_matrix.
        Similarly constructed ndarrays can also be used.
    class_names: list
        An ordered list of class names, in the order they index the given confusion matrix.
    figsize: tuple
        A 2-long tuple, the first value determining the horizontal size of the ouputted figure,
        the second determining the vertical size. Defaults to (10,7).
    fontsize: int
        Font size for axes labels. Defaults to 14.

    Returns
    -------
    matplotlib.figure.Figure
        The resulting confusion matrix figure
    """
    df_cm = pd.DataFrame(confusion_matrix, index=class_names, columns=class_names)
    fig, ax = plt.subplots(figsize=figsize)
    heatmap = sns.heatmap(df_cm, annot=False, cmap="Blues")
    heatmap.set(ylabel="True label", xlabel="Predicted label")

    return fig


def plot_accuracy_development(history, _run):
    fig, ax = plt.subplots()
    writer = FFMpegWriter(fps=1)
    filename = "accuracy_movie.mp4"
    with writer.saving(fig, filename, 600):
        acc = history.history["acc"]
        x = list(range(1, len(acc) + 1))
        y = acc
        ax.set(xlim=[0.9, len(acc) + 0.1], ylim=[0, 1], xlabel="epoch", ylabel="accuracy")
        [acc_line] = ax.plot(x, y, "o-")

        for i in range(1, len(acc) + 1):
            acc_line.set_data(x[:i], y[:i])

            writer.grab_frame()

    _run.add_artifact(filename=filename, name="accuracy_movie")


def write_csv_as_text(history, _run):
    filename = "history.txt"
    with open(filename, "w") as handle:
        handle.write("acc, loss\n")
        for acc, loss in zip(history.history["acc"], history.history["loss"]):
            handle.write(f"{acc}, {loss}\n")

    _run.add_artifact(filename=filename, name="history")


ex = Experiment("example")
ex.captured_out_filter = apply_backspaces_and_linefeeds

ex.observers.append(MongoObserver.create(url=None, db_name="incense_test"))


@ex.config
def hyperparameters():
    optimizer = "sgd"  # lgtm [py/unused-local-variable]
    epochs = 1  # lgtm [py/unused-local-variable]
    seed = 0


def make_model():
    model = tf.keras.models.Sequential(
        [
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(512, activation=tf.nn.relu),
            tf.keras.layers.Dropout(rate=0.2),
            tf.keras.layers.Dense(10, activation=tf.nn.softmax),
        ]
    )
    return model


@ex.command
def conduct(epochs, optimizer, _run):
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    x_train = x_train / 255.0
    x_test = x_test / 255.0

    model = make_model()

    model.compile(loss="sparse_categorical_crossentropy", optimizer=optimizer, metrics=["accuracy"])

    metrics_logger = MetricsLogger(_run)

    history = model.fit(x_train, y_train, epochs=epochs, callbacks=[metrics_logger], verbose=0)

    predictions = model.predict(x_test)

    predictions = predictions.argmax(axis=1)
    predictions_df = pd.DataFrame({"predictions": predictions, "targets": y_test})
    filename = "predictions_df.pickle"
    predictions_df.to_pickle(filename)
    _run.add_artifact(filename, name="predictions_df")

    filename = "predictions.csv"
    predictions_df.to_csv(filename, index=False)
    _run.add_artifact(filename, name="predictions")

    fig = plot_confusion_matrix(confusion_matrix(y_test, predictions), class_names=list(range(10)))
    filename = "confusion_matrix.png"
    fig.savefig(filename)
    _run.add_artifact(filename, name="confusion_matrix")

    filename = "confusion_matrix.pdf"
    fig.savefig(filename)
    _run.add_artifact(filename, name="confusion_matrix_pdf")

    plot_accuracy_development(history, _run)
    write_csv_as_text(history, _run)
    scalar_results = model.evaluate(x_test, y_test, verbose=0)

    results = dict(zip(model.metrics_names, scalar_results))
    print("Final test results")
    print(results)
    for metric, value in results.items():
        _run.log_scalar(f"test_{metric}", value)

    return results["acc"]


if __name__ == "__main__":
    ex.run("conduct")
    ex.run("conduct", config_updates={"epochs": 3})
    ex.run("conduct", config_updates={"optimizer": "adam"})

import json
import numpy as np
import pickle
import random
from pathlib import Path
import typer
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics


def evaluate_model(
    data_dir: Path, model_path: Path, scores_file: Path, roc_file: Path
) -> None:
    # reading parameters
    params = yaml.safe_load(open("params.yaml"))["model"]
    random.seed(params["seed"])

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    test_x = np.load(data_dir / "test_x.npy")
    test_y = np.load(data_dir / "test_y.npy")

    probas = model.predict_proba(test_x)
    predictions = model.predict(test_x)

    # Scores
    acc = metrics.accuracy_score(test_y, predictions)

    with open(scores_file, "w") as f:
        json.dump({"acc": acc}, f, indent=4)

    # Plots
    fpr = dict()
    tpr = dict()
    roc_thresholds = dict()

    fpr, tpr, roc_thresholds = metrics.roc_curve(test_y, probas[:, 1])

    with open(roc_file, "w") as f:
        json.dump(
            {
                "roc": [
                    {"fpr": fp, "tpr": tp, "threshold": t}
                    for fp, tp, t in zip(fpr, tpr, roc_thresholds)
                ]
            },
            f,
            indent=4,
        )


if __name__ == "__main__":
    typer.run(evaluate_model)

import torch
from torchmetrics.classification import BinaryPrecision, BinaryRecall, BinaryAccuracy


def calculate_metrics_torch(y_true, y_pred):
    """
    Calculate precision, recall, and accuracy using torchmetrics.

    Parameters:
        y_true (torch.Tensor): True labels (tensor of 0s and 1s)
        y_pred (torch.Tensor): Predicted labels (tensor of 0s and 1s)
    
    Returns:
        dict: A dictionary containing precision, recall, and accuracy
    """
    y_true = y_true.int() if not isinstance(y_true, torch.Tensor) else y_true
    y_pred = y_pred.int() if not isinstance(y_pred, torch.Tensor) else y_pred

    precision_metric = BinaryPrecision()
    recall_metric = BinaryRecall()
    accuracy_metric = BinaryAccuracy()

    precision = precision_metric(y_pred, y_true)
    recall = recall_metric(y_pred, y_true)
    accuracy = accuracy_metric(y_pred, y_true)

    return {
        "precision": precision.item(),
        "recall": recall.item(),
        "accuracy": accuracy.item()
    }

if __name__ == "__main__":
    threshold = 0.8

    actual_similarity_score = torch.tensor([0.5, 0.3, 0.2, 0.9, 0.9])
    y_true = (actual_similarity_score >= threshold).int()

    pred_similarity_score = torch.tensor([0.2, 0.66,  0.3, 0.1, 0.89])
    y_pred = (pred_similarity_score >= threshold).int()

    metrics = calculate_metrics_torch(y_true, y_pred)
    print("Metrics:", metrics)

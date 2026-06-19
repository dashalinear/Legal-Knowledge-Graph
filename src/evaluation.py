from typing import List, Dict, Tuple


def compute_f1(
    gold: List[Dict],
    pred: List[Dict],
) -> Tuple[float, float, float]:
    """
    Compute precision, recall, F1 for article extraction
    on a simple span / article-number match basis.
    """
    gold_set = {(g["start"], g["end"], tuple(g["article_numbers"])) for g in gold}
    pred_set = {(p["start"], p["end"], tuple(p["article_numbers"])) for p in pred}

    tp = len(gold_set & pred_set)
    fp = len(pred_set - gold_set)
    fn = len(gold_set - pred_set)

    precision = tp / (tp + fp) if tp + fp > 0 else 0.0
    recall = tp / (tp + fn) if tp + fn > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall > 0
        else 0.0
    )

    return precision, recall, f1
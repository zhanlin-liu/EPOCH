"""Rule-based Iris species classifier.

Rules use sepal and petal measurements to classify into:
- setosa, versicolor, virginica
"""


def classify(sample: dict) -> str:
    """Classify an iris sample using rule-based logic.

    Args:
        sample: dict with sepal_length, sepal_width, petal_length, petal_width

    Returns:
        Predicted class label string.
    """
    petal_length = sample["petal_length"]
    petal_width = sample["petal_width"]

    # Rule 1: Setosa has distinctly small petals
    if petal_length < 2.5:
        return "setosa"

    sepal_width = sample["sepal_width"]

    # Rule 2: Long petals indicate virginica
    if petal_length >= 5.0:
        return "virginica"

    # Rule 3: Wide petals with narrow sepals indicate virginica
    # (versicolor with wide petals tends to also have wide sepals)
    if petal_width >= 1.7 and sepal_width <= 3.0:
        return "virginica"

    # Default: versicolor
    return "versicolor"

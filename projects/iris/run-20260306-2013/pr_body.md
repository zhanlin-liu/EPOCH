## Round 1: Baseline Establishment

### Configuration
- **Task**: Rule-based Iris species classification
- **Features**: sepal_length, sepal_width, petal_length, petal_width
- **Classes**: setosa, versicolor, virginica
- **Data**: 105 train (35/class), 45 eval (15/class)

### Baseline Rules
1. `petal_length < 2.5` → setosa
2. `petal_length > 5.0` → virginica
3. `petal_width > 1.5` → virginica
4. Default → versicolor

### Metrics

| Metric | Value |
|--------|-------|
| train_accuracy | 0.9524 (100/105) |
| eval_accuracy | 0.9778 (44/45) |
| train_failures | 5 |
| eval_failures | 1 |

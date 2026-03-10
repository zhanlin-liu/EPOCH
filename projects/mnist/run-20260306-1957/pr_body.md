## Round 1: Baseline Establishment

### Configuration
- **Model**: MobileNetV2 (pretrained ImageNet, classifier head fine-tuned)
- **Dataset**: MNIST subset (10 classes, 200 train, 60 eval)
- **Hyperparameters**: optimizer=adam, learning_rate=0.001
- **Training**: 3 epochs, seed=42, device=mps

### Metrics

| Metric | Value |
|--------|-------|
| eval_accuracy | 0.5333 |
| eval_loss | 1.5122 |
| train_accuracy | 0.6050 |
| train_loss | 1.3848 |
| train_eval_gap | 0.0717 |

### Observations
- Loss still decreasing at epoch 3 — model is underfitting
- Train-eval gap is small (0.07) — no overfitting concern
- Conservative baseline leaves significant room for improvement

---
name: xai-visualization
description: "Explainable AI visualization patterns with SHAP and LIME for audit transparency"
user-invocable: false
---

# Skill: XAI Visualization

Visualización de explicabilidad con SHAP y LIME.

---

## SHAP Summary Plot

```python
import shap
import matplotlib.pyplot as plt
from pathlib import Path


def generate_shap_summary(
    model,
    X_test,
    feature_names: list[str],
    output_path: Path,
) -> None:
    """Generate SHAP summary plot."""

    # TreeExplainer for XGBoost
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    # Summary plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(
        shap_values,
        X_test,
        feature_names=feature_names,
        show=False,
    )
    plt.tight_layout()
    plt.savefig(output_path / "shap_summary.png", dpi=150)
    plt.close()
```

---

## SHAP Waterfall (Individual)

```python
def generate_shap_waterfall(
    model,
    X_instance,
    feature_names: list[str],
    output_path: Path,
    instance_id: str,
) -> None:
    """Generate SHAP waterfall plot for single instance."""

    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X_instance)

    plt.figure(figsize=(10, 6))
    shap.waterfall_plot(shap_values[0], show=False)
    plt.title(f"SHAP Explanation: {instance_id}")
    plt.tight_layout()
    plt.savefig(output_path / f"shap_waterfall_{instance_id}.png", dpi=150)
    plt.close()
```

---

## SHAP Force Plot (Interactive HTML)

```python
def generate_shap_force_html(
    model,
    X_test,
    output_path: Path,
) -> None:
    """Generate interactive SHAP force plot."""

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    # Force plot (interactive)
    force_plot = shap.force_plot(
        explainer.expected_value,
        shap_values,
        X_test,
    )

    # Save as HTML
    shap.save_html(output_path / "shap_force.html", force_plot)
```

---

## LIME Explanation

```python
from lime.lime_tabular import LimeTabularExplainer
import numpy as np


def generate_lime_explanation(
    model,
    X_train: np.ndarray,
    X_instance: np.ndarray,
    feature_names: list[str],
    class_names: list[str],
    output_path: Path,
    instance_id: str,
) -> dict:
    """Generate LIME explanation for single instance."""

    explainer = LimeTabularExplainer(
        X_train,
        feature_names=feature_names,
        class_names=class_names,
        mode="classification",
    )

    exp = explainer.explain_instance(
        X_instance,
        model.predict_proba,
        num_features=10,
    )

    # Save as HTML
    exp.save_to_file(output_path / f"lime_{instance_id}.html")

    # Return as dict for programmatic use
    return {
        "prediction": exp.predict_proba,
        "local_explanation": exp.as_list(),
        "intercept": exp.intercept,
    }
```

---

## Risk Distribution Chart

```python
import plotly.express as px
import pandas as pd


def generate_risk_distribution(
    vulnerabilities: list[dict],
    output_path: Path,
) -> None:
    """Generate risk distribution chart."""

    df = pd.DataFrame(vulnerabilities)

    # Pie chart by severity
    fig = px.pie(
        df,
        names="severity",
        title="Vulnerability Distribution by Severity",
        color="severity",
        color_discrete_map={
            "CRITICAL": "#dc3545",
            "HIGH": "#fd7e14",
            "MEDIUM": "#ffc107",
            "LOW": "#28a745",
        },
    )
    fig.write_html(output_path / "risk_distribution.html")
    fig.write_image(output_path / "risk_distribution.png")
```

---

## Feature Importance Bar Chart

```python
def generate_feature_importance(
    model,
    feature_names: list[str],
    output_path: Path,
) -> None:
    """Generate feature importance bar chart."""

    importance = model.feature_importances_
    sorted_idx = np.argsort(importance)[::-1]

    fig = px.bar(
        x=[feature_names[i] for i in sorted_idx[:10]],
        y=[importance[i] for i in sorted_idx[:10]],
        title="Top 10 Feature Importances",
        labels={"x": "Feature", "y": "Importance"},
    )
    fig.write_html(output_path / "feature_importance.html")
    fig.write_image(output_path / "feature_importance.png")
```

---

## Tríada de Evidencia Completa

```python
@dataclass
class EvidenceTriad:
    """Complete evidence for a single prediction."""

    cve_id: str
    prediction: str
    confidence: float
    shap_values: dict[str, float]
    lime_rules: list[tuple[str, float]]
    feature_values: dict[str, float]


def generate_evidence_triad(
    model,
    X_instance: np.ndarray,
    feature_names: list[str],
    cve_id: str,
    output_path: Path,
) -> EvidenceTriad:
    """Generate complete evidence triad for auditing."""

    # Prediction
    prediction = model.predict(X_instance.reshape(1, -1))[0]
    proba = model.predict_proba(X_instance.reshape(1, -1))[0]
    confidence = max(proba)

    # SHAP
    explainer = shap.TreeExplainer(model)
    shap_vals = explainer.shap_values(X_instance.reshape(1, -1))[0]
    shap_dict = dict(zip(feature_names, shap_vals))

    # LIME
    lime_exp = generate_lime_explanation(...)

    # Save visualizations
    generate_shap_waterfall(model, X_instance, feature_names, output_path, cve_id)

    return EvidenceTriad(
        cve_id=cve_id,
        prediction=["LOW", "MEDIUM", "HIGH", "CRITICAL"][prediction],
        confidence=confidence,
        shap_values=shap_dict,
        lime_rules=lime_exp["local_explanation"],
        feature_values=dict(zip(feature_names, X_instance)),
    )
```

---

## Streamlit Dashboard Integration

```python
import streamlit as st
import shap


def render_xai_dashboard(evidence: EvidenceTriad) -> None:
    """Render XAI explanation in Streamlit."""

    st.header(f"Explanation: {evidence.cve_id}")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Prediction", evidence.prediction)
        st.metric("Confidence", f"{evidence.confidence:.1%}")

    with col2:
        st.subheader("Top SHAP Factors")
        for feature, value in sorted(
            evidence.shap_values.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]:
            st.write(f"- {feature}: {value:+.3f}")

    st.subheader("LIME Rules")
    for rule, weight in evidence.lime_rules[:5]:
        st.write(f"- {rule} → {weight:+.3f}")
```

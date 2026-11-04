import os
import gradio as gr
import requests

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

# Group features logically for better UI organization
FEATURE_GROUPS = {
    "Mean Features (Overall Size & Texture)": [
        "radius_mean", "texture_mean", "perimeter_mean", "area_mean", "smoothness_mean",
        "compactness_mean", "concavity_mean", "concave points_mean", "symmetry_mean", "fractal_dimension_mean"
    ],
    "Standard Error (SE) Features": [
        "radius_se", "texture_se", "perimeter_se", "area_se", "smoothness_se",
        "compactness_se", "concavity_se", "concave points_se", "symmetry_se", "fractal_dimension_se"
    ],
    "Worst Features (Mean of 3 Largest Values)": [
        "radius_worst", "texture_worst", "perimeter_worst", "area_worst", "smoothness_worst",
        "compactness_worst", "concavity_worst", "concave points_worst", "symmetry_worst", "fractal_dimension_worst"
    ]
}
"""
Adding this comment to ensure docker takes the new updated file
"""
# Flattened list for backend payload mapping
FEATURE_NAMES = [name for group in FEATURE_GROUPS.values() for name in group]

# Realistic default values based on a typical benign tumor profile
DEFAULT_VALUES = [
    13.5, 19.0, 87.0, 560.0, 0.095, 0.100, 0.070, 0.035, 0.180, 0.062,  # Mean
    0.350, 1.200, 2.400, 25.0, 0.007, 0.025, 0.030, 0.012, 0.020, 0.003, # SE
    15.0, 25.0, 98.0, 700.0, 0.125, 0.220, 0.190, 0.090, 0.270, 0.080   # Worst
]

# Example presets for quick testing
SAMPLE_BENIGN = DEFAULT_VALUES
SAMPLE_MALIGNANT = [
        20.5, 20.0, 135.0, 1260.0, 0.110, 0.160, 0.190, 0.105, 0.190, 0.060,
        0.600, 1.500, 4.500, 75.0, 0.008, 0.030, 0.040, 0.015, 0.025, 0.004,
        25.0, 28.0, 175.0, 2000.0, 0.150, 0.400, 0.450, 0.180, 0.300, 0.095
        ]

def predict_tumor(*values):
    payload = dict(zip(FEATURE_NAMES, values))
    try:
        response = requests.post(f"{BACKEND_URL}/predict", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        return f"Diagnosis: {result['diagnosis']} | Malignant probability: {result['malignant_probability']}"
    except requests.exceptions.RequestException as e:
        return f"Error contacting backend: {e}"

with gr.Blocks(title="Breast Cancer Predictor") as demo:
    gr.Markdown("#Breast Cancer Diagnostic Predictor")
    gr.Markdown("Enter or adjust tumor measurements below. Use the **Examples** at the bottom to instantly load typical Benign or Malignant profiles.")

    input_components = []
    
    # Create accordions for each feature category
    for group_name, names in FEATURE_GROUPS.items():
        with gr.Accordion(group_name, open=(group_name == "Mean Features (Overall Size & Texture)")):
            with gr.Row():
                for name in names:
                    default_val = DEFAULT_VALUES[FEATURE_NAMES.index(name)]
                    # minimum=0.0 prevents invalid negative medical values
                    comp = gr.Number(label=name, value=default_val, minimum=0.0)
                    input_components.append(comp)

    predict_btn = gr.Button("Predict Diagnosis", variant="primary")
    output_box = gr.Textbox(label="Prediction Result")

    predict_btn.click(
        fn=predict_tumor,
        inputs=input_components,
        outputs=output_box
    )

    # Add one-click example profiles
    gr.Examples(
        examples=[SAMPLE_BENIGN, SAMPLE_MALIGNANT],
        inputs=input_components,
        label="Quick Load Sample Profiles (Benign vs Malignant)"
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

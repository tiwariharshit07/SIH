from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)


# ============================================================
# LOAD TRAINED MODELS
# ============================================================

severity_classifier = joblib.load(
    "models/severity_classifier.pkl"
)

severity_score_model = joblib.load(
    "models/severity_score_model.pkl"
)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "citizen_severity",
    "nearby_reports",
    "disaster_type",
    "population_density",
    "distance_critical_infra",
    "alert_intensity",
    "people_affected",
    "historical_risk"
]


# ============================================================
# NORMALIZE FRONTEND INPUT
# ============================================================

def normalize_citizen_severity(value):

    value = str(value).strip()

    mapping = {
        "Low": "Low",
        "Medium": "Medium",
        "High": "High",

        # Frontend value
        "High / Critical": "High",
        "HIGH / CRITICAL": "High",
        "High/Critical": "High"
    }

    return mapping.get(value, "Medium")


def normalize_disaster_type(value):

    value = str(value).strip()

    mapping = {
        "Earthquakes": "Earthquake",
        "Earthquake": "Earthquake",

        "Forest Fires": "Forest Fire",
        "Forest Fire": "Forest Fire",

        "Urban Fires": "Urban Fire",
        "Urban Fire": "Urban Fire",

        "Floods": "Flood",
        "Flood": "Flood",

        "Cyclones": "Cyclone",
        "Cyclone": "Cyclone",

        "Heatwaves": "Heatwave",
        "Heatwave": "Heatwave",

        "Landslides": "Landslide",
        "Landslide": "Landslide",

        "Lightning": "Lightning",

        "Medical Emergency": "Medical Emergency"
    }

    return mapping.get(value, value)


# ============================================================
# SCORE → SEVERITY
#
# THIS IS THE SINGLE SOURCE OF TRUTH
# ============================================================

def score_to_severity(score):

    if score < 17:
        return "Low"

    elif score < 34:
        return "Moderate"

    elif score < 50:
        return "Medium"

    elif score < 67:
        return "High"

    elif score < 84:
        return "Severe"

    else:
        return "Critical"


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "Severity AI Engine is running"
    })


# ============================================================
# PREDICT SEVERITY
# ============================================================

@app.route("/predict-severity", methods=["POST"])
def predict_severity():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "No JSON data received"
            }), 400


        # =====================================================
        # CHECK REQUIRED FEATURES
        # =====================================================

        for feature in FEATURES:

            if feature not in data:

                return jsonify({
                    "success": False,
                    "error": f"Missing field: {feature}"
                }), 400


        # =====================================================
        # NORMALIZE INPUTS
        # =====================================================

        citizen_severity = normalize_citizen_severity(
            data["citizen_severity"]
        )

        disaster_type = normalize_disaster_type(
            data["disaster_type"]
        )


        # =====================================================
        # CREATE MODEL INPUT
        # =====================================================

        input_data = pd.DataFrame([{

            "citizen_severity":
                citizen_severity,

            "nearby_reports":
                float(data["nearby_reports"]),

            "disaster_type":
                disaster_type,

            "population_density":
                float(data["population_density"]),

            "distance_critical_infra":
                float(data["distance_critical_infra"]),

            "alert_intensity":
                float(data["alert_intensity"]),

            "people_affected":
                float(data["people_affected"]),

            "historical_risk":
                float(data["historical_risk"])

        }])


        # =====================================================
        # EXACT FEATURE ORDER
        # =====================================================

        input_data = input_data[FEATURES]


        # =====================================================
        # AI SCORE
        # =====================================================

        predicted_score = severity_score_model.predict(
            input_data
        )[0]


        # =====================================================
        # KEEP SCORE BETWEEN 0 AND 100
        # =====================================================

        severity_score = max(
            0,
            min(
                100,
                float(predicted_score)
            )
        )


        severity_score = round(
            severity_score,
            2
        )


        # =====================================================
        # IMPORTANT
        #
        # DO NOT USE THE CLASSIFIER'S RESULT FOR DISPLAY.
        #
        # SCORE IS THE SOURCE OF TRUTH.
        # =====================================================

        severity_level = score_to_severity(
            severity_score
        )


        # =====================================================
        # OPTIONAL:
        # KEEP CLASSIFIER PREDICTION FOR DEBUGGING
        # =====================================================

        classifier_prediction = str(
            severity_classifier.predict(
                input_data
            )[0]
        )


        # =====================================================
        # LOG
        # =====================================================

        print()
        print("=" * 60)
        print("AI SEVERITY PREDICTION")
        print("=" * 60)

        print(
            "Citizen Severity:",
            citizen_severity
        )

        print(
            "Disaster Type:",
            disaster_type
        )

        print(
            "AI Score:",
            severity_score
        )

        print(
            "Final Severity:",
            severity_level
        )

        print(
            "Classifier Prediction:",
            classifier_prediction
        )

        print("=" * 60)
        print()


        # =====================================================
        # RESPONSE
        # =====================================================

        return jsonify({

            "success": True,

            "severity_score":
                severity_score,

            "severity_level":
                severity_level

        })


    except Exception as e:

        print(
            "SEVERITY AI ERROR:",
            str(e)
        )

        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


# ============================================================
# START SERVER
# ============================================================
if __name__ == "__main__":
    import os

    print("=" * 60)
    print("DISASTER SEVERITY AI API")
    print("=" * 60)

    print()
    print("Loading AI models...")

    print("Severity classifier loaded!")
    print("Severity score model loaded!")

    print()
    print("API running at:")

    port = int(os.environ.get("PORT", 5001))
    print(f"http://127.0.0.1:{port}")

    print("=" * 60)

    app.run(host="0.0.0.0", port=port, debug=False)
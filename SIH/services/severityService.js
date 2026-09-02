const SEVERITY_AI_URL =
    `${process.env.ML_API_URL}/predict-severity`;

async function predictSeverity(inputs) {

    try {

                console.log("Calling ML API at:", SEVERITY_AI_URL); // DEBUG LINE  

        const response = await fetch(
            SEVERITY_AI_URL,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    citizen_severity:
                        inputs.citizenSeverity,

                    nearby_reports:
                        inputs.nearbyReports,

                    disaster_type:
                        inputs.disasterType,

                    population_density:
                        inputs.populationDensity,

                    distance_critical_infra:
                        inputs.distanceCriticalInfra,

                    alert_intensity:
                        inputs.alertIntensity,

                    people_affected:
                        inputs.peopleAffected,

                    historical_risk:
                        inputs.historicalRisk

                })
            }
        );

         // NEW: check response before parsing JSON
        if (!response.ok) {
            const text = await response.text();
            console.error("ML API returned non-OK status:", response.status, text.slice(0, 200));
            throw new Error(`Severity AI returned status ${response.status}`);
        }
         

        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Severity AI prediction failed"
            );

        }


        return {

            severityScore:
                data.severity_score,

            severityLevel:
                data.severity_level

        };


    } catch (error) {

        console.error(
            "Severity AI error:",
            error.message
        );

        throw error;

    }

}


module.exports = {
    predictSeverity
};
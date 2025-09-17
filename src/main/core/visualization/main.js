const stateLookup = {
    "01": "alabama",
    "02": "alaska",
    "04": "arizona",
    "05": "arkansas",
    "06": "california",
    "08": "colorado",
    "09": "connecticut",
    "10": "delaware",
    "11": "district_of_columbia",
    "12": "florida",
    "13": "georgia",
    "15": "hawaii",
    "16": "idaho",
    "17": "illinois",
    "18": "indiana",
    "19": "iowa",
    "20": "kansas",
    "21": "kentucky",
    "22": "louisiana",
    "23": "maine",
    "24": "maryland",
    "25": "massachusetts",
    "26": "michigan",
    "27": "minnesota",
    "28": "mississippi",
    "29": "missouri",
    "30": "montana",
    "31": "nebraska",
    "32": "nevada",
    "33": "new_hampshire",
    "34": "new_jersey",
    "35": "new_mexico",
    "36": "new_york",
    "37": "north_carolina",
    "38": "north_dakota",
    "39": "ohio",
    "40": "oklahoma",
    "41": "oregon",
    "42": "pennsylvania",
    "44": "rhode_island",
    "45": "south_carolina",
    "46": "south_dakota",
    "47": "tennessee",
    "48": "texas",
    "49": "utah",
    "50": "vermont",
    "51": "virginia",
    "53": "washington",
    "54": "west_virginia",
    "55": "wisconsin",
    "56": "wyoming"
};

function toTitleCase(str) {
  if (!str) {
    return "";
  }
  return str.toLowerCase().replace(/\b\w/g, function(char) {
    return char.toUpperCase();
  });
}


document.addEventListener('DOMContentLoaded', () => {

    const center = [42, -96];
    const map = L.map('map').setView(center, 4);

    // Basemap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 10
    }).addTo(map);

    let selectedLayer = null; // Track highlighted area

    let geojsonCounties = null;

    let shadingMode = "raw";

    let nationalAverages = {};

    let selectedDemographic = null;

    document.getElementById("scale-select").addEventListener("change", e => {
        shadingMode = e.target.value;
        if (geojsonCounties) geojsonCounties.setStyle(style);

        const legendDiv = document.querySelector('.legend');
        if (legendDiv) updateLegend(legendDiv);
    });

    fetch("counties.json")
        .then(res => res.json())
        .then(countyData => {

            // Compute national averages
            fetch("nation.json")
                .then(res => res.json())
                .then(data => {
                    nationalAverages = data.demographics;
                    // Load geometries
                    fetch("us-states.json")
                        .then(res => res.json())
                        .then(topoData => {
                            const counties = topojson.feature(topoData, topoData.objects.counties);
                            // Attach demographics
                            counties.features.forEach(f => {
                                f.properties.demographics = countyData[f.id]?.demographics || null;
                                f.properties.name = countyData[f.id]?.name || "";
                                f.properties.population = countyData[f.id]?.population || 0;
                                const fp = f.id.substring(0, 2);
                                f.properties.state = stateLookup[fp];
                            });
                            // Add GeoJSON layer
                            geojsonCounties = L.geoJSON(counties, { style, onEachFeature }).addTo(map);
                        });
                });
        });

    function getColor(value, mode = "relative") {
        if (mode === "relative") {
            return value > 2.0 ? "#800026" :
                   value > 1.5 ? "#BD0026" :
                   value > 1.2 ? "#E31A1C" :
                   value > 1.0 ? "#FC4E2A" :
                   value > 0.8 ? "#FD8D3C" :
                   value > 0.5 ? "#FEB24C" :
                                 "#FFEDA0" ; 
        }
        else if (mode === "raw") {
            return value > 0.95 ? "#520016" :
                   value > 0.85 ? "#680020" :
                   value > 0.75 ? "#800026" :
                   value > 0.50 ? "#BD0026" : 
                   value > 0.25 ? "#E31A1C" : 
                   value > 0.10 ? "#FC4E2A" : 
                   value > 0.05 ? "#FD8D3C" : 
                   value > 0.01 ? "#FEB24C" : 
                                  "#FFEDA0" ;
        }
        else if (mode === "count") {
            return value > 800000 ? "#001900" :
                   value > 400000 ? "#002600" :
                   value > 100000 ? "#003300" :
                   value > 50000  ? "#0D4D0D" :
                   value > 25000  ? "#1A661A" :
                   value > 10000  ? "#268026" :
                   value > 5000   ? "#339933" :
                   value > 2500   ? "#4DB34d" :
                   value > 1000   ? "#80D580" :
                   value > 500    ? "#99DD99" :
                   value > 250    ? "#B2E5B2" :
                   value > 100    ? "#CCEECC" :
                   value > 0      ? "#E6F7E6" :
                                    "#FFFFFF" ;
        }
    }

    function getDemographicCategory(demo) {
        switch (demo) {
            case "White" : 
            case "Black" : 
            case "Hispanic" : 
            case "Asian" :
            case "Mixed" :
            case "Other" :
                return "race_and_ethnicity";
            case "Married" :
            case "Single Female" :
            case "Single Male" :
            case "One-Person" : 
            case "Other Non-Family" :
                return "household_types";
            case "Healthcare" :
            case "Retail" :
            case "Manufacturing" :
            case "Education" :
            case "Hospitality" :
            case "Professional" :
            case "Construction" :
            case "Other Services" :
            case "Government" :
            case "Finance & Insurance" :
            case "Administrative" :
            case "Transportation" :
            case "Wholesalers" :
            case "Entertainment" :
            case "Information" :
            case "Real estate" :
            case "Agriculture" :
            case "Utilities" :
            case "Oil & Gas, and Mining" :
            case "Management" :
                return "industries";
            case "Doctorate" :
            case "Professional" :
            case "Master's" :
            case "Bachelor's" :
            case "Associate's" :
            case "Some College" :
            case "High School" :
            case "Some H.S." :
            case "Less than H.S." :
            case "None" :
                return "educational_attainment";
        }
    }

    function style(feature) {
        if (!selectedDemographic || !feature.properties.demographics) {
            return {
                fillColor: "#cccccc",
                weight: 1,
                opacity: 1,
                color: "#333",
                fillOpacity: 0.6,
                interactive: true // <-- make sure polygons can be clicked
            };
        }

        const countyPercent = feature.properties.demographics[getDemographicCategory(selectedDemographic)][selectedDemographic] || 0;
        
        let colorValue;
        if (shadingMode === "raw") {
            colorValue = countyPercent;
        }
        else if (shadingMode === "relative") {
            const nationalPercent = nationalAverages[getDemographicCategory(selectedDemographic)][selectedDemographic] || 0.0001;
            colorValue = countyPercent / nationalPercent;
        }
        else if (shadingMode === "count") {
            colorValue = countyPercent * feature.properties.population;
        }
        return {
            fillColor: getColor(colorValue, shadingMode),
            weight: 1,
            opacity: 1,
            color: "#333",
            fillOpacity: 0.7
        };
    }

    document.getElementById("demographic-select").addEventListener("change", (e) => {
        selectedDemographic = e.target.value;
        if (geojsonCounties) geojsonCounties.setStyle(style);

        if (selectedDemographic) {
            if (!legendAdded) {
                legend.addTo(map);
                legendAdded = true;
            }
            else {
                const legendDiv = document.querySelector('.legend');
                if (legendDiv) updateLegend(legendDiv);
            }
        }
        else if (legendAdded) {
            // Remove legend if nothing selected
            legend.remove();
            legendAdded = false;
        }
    });

    function formatDemographics(demo) {
        let html = '';
        for (const category in demo) {
            html += `<b>${toTitleCase(category).replace(/_/g, " ")}</b><ul>`;
            const values = demo[category];
            for (const key in values) {
                if (typeof values[key] === 'object') {
                    html += `<li>${key}:<ul>`;
                    for (const subkey in values[key]) {
                        const val = values[key][subkey];
                        html += `<li>${subkey}: ${typeof val === 'number' ? val.toFixed(5) : val}</li>`;
                    }
                    html += `</ul></li>`;
                }
                else {
                    const val = values[key];
                    html += `<li>${key}: ${typeof val === 'number' ? val.toFixed(5) : val}</li>`;
                }
            }
            html += '</ul>';
        }
        return html;
    }

    function highlightFeature(e) {
        const props = e.target.feature.properties;

        const fips = e.target.feature.id;
        const state = props.state;

        console.log(fips, state);

        if (!fips || !state) {
            console.error("Missing FIPS or State:", props);
            return;
        }
        
        fetch(`/src/main/resources/${state}/counties/${fips}.json`)
            .then(res => res.json())
            .then(data => {
                const infobox = document.getElementById("infobox");
                infobox.innerHTML = `
                    <b>${data.name}</b><br>
                    Population: ${data.population}<br>
                    Demographics: <br>
                    ${formatDemographics(data.demographics)}
                `;
                infobox.scrollTop = 0;
            })
            .catch(err => console.error("Failed to load county JSON", err));

        if (selectedLayer) {
            geojsonCounties.resetStyle(selectedLayer);
        }
        selectedLayer = e.target;
        selectedLayer.setStyle({
            weight: 3,
            color: "#ff7800",
            fillOpacity: 0.5
        });
        selectedLayer.bringToFront();
    }

    function onEachFeature(feature, layer) {
        layer.on({
            click: highlightFeature
        });
    }

    document.getElementById("reset-button").addEventListener("click", () => {
        resetView();
    });

    function resetView() {
        // Reset camera
        map.setView(center, 4); // reset to default center & zoom
        // Reset demographic select
        const select = document.getElementById("demographic-select");
        if (select) {
            select.value = "";
            select.dispatchEvent(new Event('change'));
        }
        selectedDemographic = "";
        // Remove fill colors
        if (geojsonCounties) {
            geojsonCounties.setStyle(() => ({
                fillColor: "#cccccc",
                weight: 1,
                opacity: 1,
                color: "#333",
                fillOpacity: 0.6
            }));
            geojsonCounties.resetStyle(selectedLayer);
            selectedLayer = null;
        }
        // Reset infobox text
        document.getElementById("infobox").innerHTML = "Click on a county or county-equivalent to see demographic details.";
    }

    let legend = L.control({ position: 'bottomleft' });

    legend.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'info legend');
        updateLegend(div); // initial
        return div;
    };

    let legendAdded = false;

    function updateLegend(div) {
        let grades = [];
        if (shadingMode === "relative") 
            grades = [0.50, 0.80, 1.0, 1.2, 1.5, 2]
        else if (shadingMode === "raw")
            grades = [0.0, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.85, 0.95];
        else if (shadingMode === "count")
            grades = [0, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000, 4000000, 800000];

        div.innerHTML = '';
        for (let i = 0; i < grades.length; i++) {
            const from = grades[i];
            const to = grades[i + 1];
            if (shadingMode === "relative") {
                div.innerHTML +=
                `<i style="background:${getColor(from + 0.001, shadingMode)}"></i> ` +
                from.toFixed(2) * 100 + `%` + (to ? ` &ndash; ${to.toFixed(2) * 100}% of US Average<br>` :
                    `+ of US Average`);
            }
            else if (shadingMode === "raw") {
                div.innerHTML +=
                `<i style="background:${getColor(from + 0.001, shadingMode)}"></i> ` +
                from.toFixed(2) * 100 + `%` + (to ? ` &ndash; ${to.toFixed(2) * 100}%<br>` :
                    `+`);
            }
            else if (shadingMode === "count") {
                div.innerHTML +=
                `<i style="background:${getColor(from + 0.001, shadingMode)}"></i> ` +
                from + (to ? ` &ndash; ${to} people<br>` : `+ people`);
            }
        }
    }    

});
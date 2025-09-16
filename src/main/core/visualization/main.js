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

    fetch("us-states.json")
        .then(res => res.json())
        .then(topoData => {
            const counties = topojson.feature(topoData, topoData.objects.counties);
            console.log(counties.features);
            counties.features.forEach(f => {
                const fp = f.id.substring(0, 2);
                f.properties.state = stateLookup[fp];
            });
            geojsonCounties = L.geoJSON(counties, {
                style: style,
                onEachFeature: onEachFeature
            }).addTo(map);
        });

    function style(feature) {
        return {
            fillColor: "#cccccc",
            weight: 1,
            opacity: 1,
            color: "#333",
            fillOpacity: 0.6,
            interactive: true // <-- make sure polygons can be clicked
        };
    }

    function normalizeName(str) {
        return str.toLowerCase()
                  .replace(/\s+/g, "_")
                  .replace(/[^\w_]/g, "") 
    }

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

    function getCountyFileName(countyName, state) {
        console.log(countyName);
        const base = normalizeName(countyName);
        let suffix = "_county"; // default

        if (state === "louisiana") {
            suffix = "_parish";
        }
        else if (state === "alaska") {
            if (countyName.toLowerCase().includes("borough")) suffix = "_borough";
            else if (countyName.toLowerCase().includes("census area")) suffix = "_census_area";
        }
        return base + suffix + ".json";
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
                console.log(document.getElementById("infobox").innerHTML);
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
        map.setView(center, 4); // reset to default center & zoom
        if (selectedLayer && geojsonCounties) {
            geojsonCounties.resetStyle(selectedLayer);
            selectedLayer = null;
        }
        document.getElementById("infobox").innerHTML = "Click on a county-equivalent to see demographic details.";
        console.log(countyData)
    }

});
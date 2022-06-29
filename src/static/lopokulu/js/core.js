/* Löpökulu Core JS */

const charts = [];

window.addEventListener("load", () => {
    attachAreYouSure();
    attachDTPicker();
    attachCharts();
});

/* Attaches "are you sure" dialog to all elements with data-confirm attribute */
function attachAreYouSure() {
    const elements = document.querySelectorAll("[data-confirm]");
    elements.forEach((element) => {
        element.onclick = () => {
            return confirm("Are you sure?");
        }
    });
}

/* Attaches Flatpickr DateTimePicker with a few custom options available.

Attributes:
data-dtpicker - Enables Flatpickr on element
data-dtpicker-enable-time - Enables time on Flatpickr
data-dtpicker-time-24h - Sets Flatpickr to 24h mode
*/
function attachDTPicker() {
    document.querySelectorAll("[data-dtpicker]").forEach((element) => {
        options = {"dateFormat": "Y-m-d"}
        if (element.hasAttribute("data-dtpicker-enable-time")) {
            options["dateFormat"] = "Y-m-d H:i";
            options["enableTime"] = true;
        }
        if (element.hasAttribute("data-dtpicker-time-24h")) {
            options["time_24hr"] = true;
        }
        flatpickr(element, options);
    });
}

/* Attaches ChartJS charts to every element with data-chartjs.

Attributes:
data-chartjs - Enables ChartJS for the element
data-labels - Array of labels (x axis)
data-sets - Array of ChartJS datasets
data-options - Dict of ChartJS options
data-type - Chart type
*/
function attachCharts() {
    let id_num = 0;
    document.querySelectorAll("[data-chartjs]").forEach((element) => {
        let id = "chart_" + id_num;
        element.id = id;

        let chart = new Chart(id, {
            type: element.getAttribute("data-type"),
            data: {
                labels: JSON.parse(element.getAttribute("data-labels")),
                datasets: JSON.parse(element.getAttribute("data-sets")),
            },
            options: JSON.parse(element.getAttribute("data-options")),
        });

        charts.push(chart);

        id_num++;
    });
}

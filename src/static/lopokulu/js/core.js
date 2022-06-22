/* Löpökulu Core JS */

window.addEventListener("load", () => {
    attachAreYouSure();
    attachDTPicker();
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

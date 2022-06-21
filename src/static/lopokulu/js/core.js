/* Löpökulu Core JS */

window.addEventListener("load", () => {
    attachAreYouSure();
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

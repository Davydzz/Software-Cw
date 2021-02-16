function displayDivDemo(id, elementValue) {
    document.getElementById(id).style.display = elementValue.value == "interval" ? 'block' : 'none';
}
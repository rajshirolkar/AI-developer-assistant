function toggle(name) {
    var evalDiv = document.getElementById(name);
    if (evalDiv.style.display === 'none') {
        evalDiv.style.display = "block";
    } else {
        evalDiv.style.display = "none";
    }
}
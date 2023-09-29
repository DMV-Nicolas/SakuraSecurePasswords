const copied_text = "Copiado!"

function copy(element) {

    const elementText = document.getElementById(element.value).innerHTML
    var aux = document.createElement("input");
    aux.setAttribute("value", elementText);
    document.body.appendChild(aux);
    aux.select();
    document.execCommand("copy");
    document.body.removeChild(aux);

    //VisualChanges
    element.classList.remove("btn-danger");
    element.classList.add("btn-success");
    const afterText = element.innerHTML;
    element.innerHTML = copied_text;
    setTimeout(function() {
        element.classList.remove("btn-success");
        element.classList.add("btn-danger");
        element.innerHTML = afterText;
    }, 1100);
}
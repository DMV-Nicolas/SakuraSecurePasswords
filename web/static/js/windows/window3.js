var btnAbrirPopup3 = document.getElementById('btn-abrir-popup3'),
    overlay3 = document.getElementById('overlay3'),
    popup3 = document.getElementById('popup3'),
    btnCerrarPopup3 = document.getElementById('btn-cerrar-popup3');

btnAbrirPopup3.addEventListener('click', function() {
    overlay3.classList.add('active');
    popup3.classList.add('active');
});
btnCerrarPopup3.addEventListener('click', function(e) {
    e.preventDefault();
    overlay3.classList.remove('active');
    popup3.classList.remove('active');
});
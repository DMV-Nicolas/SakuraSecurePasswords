var btnAbrirPopup4 = document.getElementById('btn-abrir-popup4'),
    overlay4 = document.getElementById('overlay4'),
    popup4 = document.getElementById('popup4'),
    btnCerrarPopup4 = document.getElementById('btn-cerrar-popup4');

btnAbrirPopup4.addEventListener('click', function() {
    overlay4.classList.add('active');
    popup4.classList.add('active');
});
btnCerrarPopup4.addEventListener('click', function(e) {
    e.preventDefault();
    overlay4.classList.remove('active');
    popup4.classList.remove('active');
});
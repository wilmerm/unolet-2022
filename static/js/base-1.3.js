/*
 * Se aplica a la plantilla base.
*/


// Variables globales.

var True = true;
var False = false;
var None = null;
var IS_PROCESS_SUBMIT = false; // Para prevenir hacer el submit más de una vez.



// Puede prevenir hacer el submit más de una vez.
$(document).on("submit", function(event) {
    // Evita hacer submit más de una vez.
    if (IS_PROCESS_SUBMIT) {
        event.preventDefault();
    } else {
        IS_PROCESS_SUBMIT = true;
    }
});



// Muestra la imágen de 'cargando' antes de cargar por completo la página.
$(window).on("beforeunload", function(event) {
    showLoader();
});



// {# Muestra la imagen de carga (espera) durante el tiempo indicado. #}
function showLoader(duration=40000) {
    $("#loader").fadeIn().delay(duration).fadeOut(duration);
}


// {# Actiava o desactiva el modo oscuro, enviado una señal al servidor #}
// {# el modo oscuro se establece en una variable de la sesión actual del usuario. #}
// {# y la plantilla html carga o no el archivo darkmode-1.1.css en función de si esta variable es True o False #}
function activeDarkMode() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText);
            window.location.reload();
        }
    };
    xhttp.open("GET", "/conf/setdarkmode/", true);
    xhttp.send();
}


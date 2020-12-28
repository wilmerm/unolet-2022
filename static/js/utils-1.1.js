/**
 * @utils scripts útiles comunes para todo el proyecto de Unolet.
 * 
 * @version 3.0
 * @author Unolet <https://www.unolet.com>
 * @copyright Unolet <https://www.unolet.com>
 * @see https://blog.unolet.com
 */

// -----------------------------------------------------------------------------
// Variables
//------------------------------------------------------------------------------

// Convensión con Python.
const None = null;
const True = true;
const False = false;

const PORCENTAJE = "PORCENTAJE";
const FIJO = "FIJO";




// Métodos abreviado.

function getById(id) {
  return document.getElementById(id);
}


function querySelector(text) {
  return document.querySelector(text);
}


function querySelectorAll(text) {
  return document.querySelectorAll(text);
}



// Método abreviado de location.href = 'url'.
function goToURL(url, newtab = false) {
  location.href = url;
}



// Muestra si está oculto u oculta si se está mostrando
// el elemento con el id indicado.
function setShowOrHide(id, display = "block") {
  var e = document.getElementById(id);
  if (e.style.display == "none") {
    e.style.display = display;
  } else {
    e.style.display = "none";
  }
}


// Retorna true si es un valor valor válido.
function is(value) {
  if (value == undefined) {
    return false;
  }
  if (isNaN(value)) {
    return false;
  }
  if (value) {
    return true;
  }
  return false;
}


// Retorna true si todos sus elementos son verdaderos.
function and(a, b) {
  if (!is(a)) {
    return false;
  }
  if (!is(b)) {
    return false;
  }
  return true;
}


// Obtiene el primer elemento que contenga un valor.
function firstOf(a, b = null) {
  if (is(a)) {
    return a;
  }
  return b;
}


function str(any) {
  return toString(any);
}


function int(number, alt_return = 0) {
  return firstOf(parseInt(number), alt_return);
}


function float(number, alt_return = 0) {
  return firstOf(parseFloat(number), alt_return);
}


// Convierte un número a texto en formato separador de miles.
function intcommaOLD(number, decimal_places = 2) {
  if (decimal_places > 0) {
    number = parseFloat(number);
  }
  return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}



function intcomma(num, decimal_places = 2) {
  /*
      Retorna un string representando el número con coma de miles.
  */
  try {
    num = parseFloat(num);
  } catch (error) {
    return "";
  }

  if (isNaN(num)) {
    return "";
  }

  let num_parts = num.toString().split(".");
  num_parts[0] = num_parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");

  if (num_parts[1] != undefined) {
    try {
      num_parts[1] = num_parts[1].slice(0, decimal_places);
    } catch (error) {
      console.warn("No se agregaron los decimales en utils.js intcomma(" + num + ", " + decimal_places + ")");
      console.warn(error);
    }
  }

  return num_parts.join(".");
}


// ----------------------------------------------------------
// CALCULOS
// ----------------------------------------------------------


/* -----------------------------------------------------
Calcula el impuesto del importe indicado, según los valores pasados.
::importe: importe al cual se desea extraer el impuesto.
::impuesto_value: valor pre-establecido del impuesto. Ej. 18
::impuesto_type: tipo de impuesto ('FIJO', 'PORCENTAJE')
--------------------------------------------------------*/

function calcularImpuesto(importe, impuesto_type = PORCENTAJE, impuesto_value = 0) {

  if (impuesto_type == PORCENTAJE) {
    return (importe * impuesto_value) / 100;
  }

  if (impuesto_type == FIJO) {
    return impuesto_value;
  }
  return 0;
}



/* -----------------------------------------------------
Extrae el impuesto del importe indicado, según los valores pasados.
::importe: importe al cual se desea extraer el impuesto.
::impuesto_value: valor pre-establecido del impuesto. Ej. 18
::impuesto_type: tipo de impuesto ('FIJO', 'PORCENTAJE')
--------------------------------------------------------*/
function extraerImpuesto(importe = 0, impuesto_type = PORCENTAJE, impuesto_value = 0) {

  importe = parseFloat(importe);
  impuesto_value = parseFloat(impuesto_value);

  if (impuesto_type == PORCENTAJE) {
    return importe / ((impuesto_value / 100) + 1)
  }

  if (impuesto_type == FIJO) {
    return importe - impuesto_value;
  }

  return importe;
}






/**
 * Muestra una alerta mensaje en la página.
 * @param {string} msg: mensaje.
 * @param {string} title: título.
 * @param {string} type: tipo de alerta (info (default), danger, warning, ...).
 * @param {string} alt_out: Alternativo en caso de que el elmento con el 
    * id = 'content-messages' no exista en el documento, se lanzará una 
    * alert(title + msg) * default, o console = console.log(title + msg).
* @param {string} id: identificador HTML que llevará el elemento creado.
* @returns {null}.
*/
function showMessage(msg = " ", title = " ", type = "info", alt_out = "alert", id = "id_message") {

  var content_div = getById("content-messages");

  if (content_div) {

    if (title) {
      msg = "<strong>" + title + "</strong>: " + msg;
    }

    btn = '<button class="close" type="button" data-dismiss="alert" aria-label="close">×</button>';

    //message_div = <div id='${id}' class='alert alert-${type} alert-dismissible alert-link' role='alert'>${btn}${msg}</div>;
    message_div = "<div id='" + id + "' class='alert alert-" + type + " alert-dismissible alert-link' role='alert'>" + btn + msg + "</div>";
    content_div.innerHTML = message_div;

  } else {

    if (alt_out == "alert") {
      alert(title + " " + msg);
    }

    else {
      console.log(title + " " + msg);
    }
  }
}



function hideMessage() {
  $("#content-messages").html("");
}



/*
Muestra un dialogo modal en pantalla, con un mensaje.
*/
function showModal(msg = "", title = "", type = "info", alt_out = "alert", id = "id_message") {
  $("#modal1 #modal-title").text(title);
  $("#modal1 #modal-body").text(msg);
  $("#modal1").modal("show");
}



// para traducciones (En proceso.)

function translate(text) {
  return text;
}

_ = translate





// Método de conveniencia para solicitar datos al servidor.
function sendData(url, type="GET", dataType="json", data=null, success=null) {
  try {
      $.ajax({
          url: url,
          type: type,
          data: data,
          dataType: dataType,
          success: success,
      });
  } catch (error) {
      console.log('sendData()');
      console.error(error);
  }
}
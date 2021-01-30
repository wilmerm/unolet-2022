/**
 * @utils scripts útiles comunes para todo el proyecto de Unolet.
 * 
 * @version 3.1
 * @author Unolet <https://www.unolet.com>
 * @copyright Unolet <https://www.unolet.com>
 * @see https://blog.unolet.com
 */


// Convensión con Python.
const None = null;
const True = true;
const False = false;
const PORCENTAJE = "PORCENTAJE";
const FIJO = "FIJO";



/**
 * Igual que location.href con opción de tiempo de espera.
 * @param {string} url URL a la cual ir, una cadena vacia recargará la página actual.
 * @param {number} timeout tiempo de espera antes de ir a dicha URL.
 */
function goTo(url, timeout=1000) {
  setTimeout(() => {
      location.href = url;
  }, timeout);
}



/**
 * Comprueba si es un valor válido y verdadero.
 * @param {any} value El valor que se desea evaluar.
 * @returns {boolean}
 */
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


/**
 * Operación lógica AND. Retorna True si todos sus valores son verdaderos.
 * @param {any} a Primer valor a comparar.
 * @param {any} b Segundo valor a comparar.
 * @returns {boolean}
 */
function and(a, b) {
  if (!is(a)) {
    return false;
  }
  if (!is(b)) {
    return false;
  }
  return true;
}


/**
 * Retorna el primer parámetro pasado que sea evaluado como verdadero.
 * Si ninguno son verdaderos retorna el último parámetro.
 * @returns {any}
 */
function firstOf(a, b, c, d, e, f, g, h, i, j, k) {
  array = [a, b, c, d, e, f, g, h, i, j, k]
  array.forEach(element => {
    if (is(element)) {
      return element;
    }
  });
  return k;
}

/**
 * Convierte el valor a tipo string.
 * @param {any} value valor que se desea convertir a string.
 * @returns {string} toString(value)
 */
function str(value) {
  return toString(value);
}


/**
 * Convierte el valor en tipo entero.
 * @param {any} value Valor que se desea convertir.
 * @param {any} alt_return Si el valor no se puede evaluar con parseInt, se retornará alt_return que default es 0.
 * @returns {number} parseInt(value) or alt_return
 */
function int(value, alt_return=0) {
  return firstOf(parseInt(value), alt_return);
}


/**
 * Convierte el valor en tipo número de coma flotante.
 * @param {any} value Valor que se desea convertir.
 * @param {any} alt_return Si el valor no se puede evaluar con parseFloat, se retornará alt_return que default es 0.
 * @returns {number} parseFloat(value) or alt_return
 */
function float(value, alt_return = 0) {
  return firstOf(parseFloat(value), alt_return);
}


/**
 * Convierte un número a número de tipo string de división de miles separado por coma.
 * @param {number} num Número que se desea convertir.
 * @param {number} decimal_places Cantidad de decimales (default=2).
 * @returns {string}
 */
function intcomma(num, decimal_places=2) {
  try {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  } catch (error) {
    return num;
  }
}



// CÁLCULOS



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
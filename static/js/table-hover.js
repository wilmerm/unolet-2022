/*
* Aplicado a las tablas mediante la clase css 'table-hover'
* que posean un tbody elemento.
* 
* Las filas (tr) deberán tener un atributo 'data-url' (opcional) con la url a 
* redirigir cuando el usuario activa (click/Enter) el item.
*
* Activa eventos de selección mediante teclas de dirección arriba/abajo.
* Activa la selección de filas mediante el evento focus.
*
*/


var SELECTED_ROW; // objeto tr seleccionado.


$(window).on("load", function() {

    // Evento 'Click'.
    $(".table-hover tbody tr").click(function(event) {
        let row = $(event.currentTarget)[0];
        if ("url" in row.dataset) {
            goToURL(row.dataset.url);
        }
    });
    
    
    // Evento al selecionar una fila.
    $(".table-hover tbody tr").focus(function(event) {
        let row = $(event.currentTarget)[0];
        SELECTED_ROW = row;
    });


    // Evento al posar el mouse encima.
    $(".table-hover tbody tr").mouseenter(function(event) {
        let row = $(event.currentTarget)[0];
        row.focus();
    });
    
    
    // Evento al precionar una tecla.
    $(".table-hover tbody tr").keyup(function(event) {
        let rows = $(event.currentTarget);
        
        // Tecla Enter.
        if (event.key == "Enter") {
            if ("url" in rows[0].dataset) {
                goToURL(rows[0].dataset.url);
            }
        }
    
        // Tecla flecha arriba. (Fila anterior).
        if (event.key == "ArrowUp") {
            let prevRow = rows.prev()[0];
            try {prevRow.focus()} catch (error) {}
        }
    
        // Tecla flecha abajo. (Siguiente fila).
        if (event.key == "ArrowDown") {
            let nextRow = rows.next()[0];
            try {nextRow.focus()} catch (error) {}
        }
    });
});



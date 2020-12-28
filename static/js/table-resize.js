/*
* Logra que a las columnas de las tablas con la clase '.table-resize' se puedan 
* cambiar de tamaño.
*/

$(window).on("load", function (event) {
    var thElm;
    var startOffset;

    Array.prototype.forEach.call(
      document.querySelectorAll(".table-resize th"),
      function (th) {
        th.style.position = 'relative';

        var grip = document.createElement('div');
        grip.innerHTML = "&nbsp;";
        grip.style.top = 0;
        grip.style.right = 0;
        grip.style.bottom = 0;
        grip.style.width = '5px';
        grip.style.position = 'absolute';
        grip.style.cursor = 'col-resize';
        grip.addEventListener('mousedown', function (e) {
            thElm = th;
            startOffset = th.offsetWidth - e.pageX;
        });

        th.appendChild(grip);
      });

    document.addEventListener('mousemove', function (e) {
      if (thElm) {
        thElm.style.width = startOffset + e.pageX + 'px';
      }
    });

    document.addEventListener('mouseup', function () {
        thElm = undefined;
    });
});
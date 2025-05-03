// Funcion Para validar el formato de fecha de tarjeta
document.addEventListener("DOMContentLoaded", function () {
  flatpickr("#fecha-exp", {
    altInput: true,
    altFormat: "m/Y",          // Lo que ve el usuario
    dateFormat: "Y-m-d",       // Lo que se envía al backend
    plugins: [
      new monthSelectPlugin({
        shorthand: true,
        dateFormat: "Y-m-d",
        altFormat: "m/Y"
      })
    ]
  });
});

// Description del product//
function changeImage(src) {
  document.getElementById("mainImage").src = src;
}

// Cambiar la cantidad de producto en el front
let quantity = 1;

function updateQuantityDisplay() {
  const input = document.getElementById("quantity");
  input.value = quantity;
}

// Aumentar la cantidad de producto en el front
function increaseQty() {
  quantity++;
  updateQuantityDisplay();
}

// Disminuir la cantidad de producto en el front
function decreaseQty() {
  if (quantity > 1) {
    quantity--;
    updateQuantityDisplay();
  }
}

//pagina de pago//

// Formatear tarjeta
function formatearTarjeta(input) {
  let valor = input.value.replace(/[^\d]/g, '');
  valor = valor.substring(0, 16);
  let formateado = valor.match(/.{1,4}/g)?.join('-') || '';
  input.value = formateado;
}
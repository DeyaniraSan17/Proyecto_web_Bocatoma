document.getElementById("formResena").addEventListener("submit", function (e) {
  const calificacion = document.querySelector('input[name="calificacion"]:checked');
  const probabilidad = document.querySelector('input[name="probabilidad"]:checked');

  if (!calificacion) {
    e.preventDefault();
    alert("Por favor selecciona una calificación de estrellas.");
  } else if (!probabilidad) {
    e.preventDefault();
    alert("Por favor selecciona tu probabilidad de regresar.");
  }
});

const carruseles = document.querySelectorAll(".carrusel");
const overlay    = document.getElementById("modalOverlay");
const modalImg   = document.getElementById("modalImg");
const cerrar     = document.getElementById("modalCerrar");
const modalPrev  = document.getElementById("modalPrev");
const modalNext  = document.getElementById("modalNext");

let imgsActuales = [];
let indexActual  = 0;

carruseles.forEach(carrusel => {
  const imagenes = carrusel.querySelector(".imagenes");
  const imgs     = carrusel.querySelectorAll("img");
  const prev     = carrusel.querySelector(".prev");
  const next     = carrusel.querySelector(".next");

  let index = 0;
  let auto  = null;

  function actualizar() {
    imagenes.style.transform = `translateX(-${index * 100}%)`;
  }

  imagenes.addEventListener("click", () => {
    imgsActuales = imgs;
    indexActual  = index;
    modalImg.src = imgs[indexActual].src;
    overlay.classList.add("activo");
  });

  imagenes.addEventListener("dblclick", (e) => {
    e.stopPropagation();
    if (auto) {
      clearInterval(auto);
      auto = null;
    } else {
      auto = setInterval(() => {
        index = index < imgs.length - 1 ? index + 1 : 0;
        actualizar();
      }, 2000);
    }
  });

  next.addEventListener("click", (e) => {
    e.stopPropagation();
    index = index < imgs.length - 1 ? index + 1 : 0;
    actualizar();
  });

  prev.addEventListener("click", (e) => {
    e.stopPropagation();
    index = index > 0 ? index - 1 : imgs.length - 1;
    actualizar();
  });
});

modalNext.addEventListener("click", (e) => {
  e.stopPropagation();
  indexActual = indexActual < imgsActuales.length - 1 ? indexActual + 1 : 0;
  modalImg.src = imgsActuales[indexActual].src;
});

modalPrev.addEventListener("click", (e) => {
  e.stopPropagation();
  indexActual = indexActual > 0 ? indexActual - 1 : imgsActuales.length - 1;
  modalImg.src = imgsActuales[indexActual].src;
});


cerrar.addEventListener("click", () => overlay.classList.remove("activo"));
overlay.addEventListener("click", (e) => {
  if (e.target === overlay) overlay.classList.remove("activo");
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") overlay.classList.remove("activo");
  if (e.key === "ArrowRight") modalNext.click();
  if (e.key === "ArrowLeft")  modalPrev.click();
});
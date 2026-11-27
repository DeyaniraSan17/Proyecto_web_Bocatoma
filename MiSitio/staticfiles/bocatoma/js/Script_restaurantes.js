const carruseles = document.querySelectorAll(".carrusel");

carruseles.forEach(carrusel => {
  const imagenes = carrusel.querySelector(".imagenes");
  const imgs = carrusel.querySelectorAll("img");
  const prev = carrusel.querySelector(".prev");
  const next = carrusel.querySelector(".next");

  let index = 0;
  let auto = null;

  function actualizar() {
    imagenes.style.transform = `translateX(-${index * 100}%)`;
  }

  imagenes.addEventListener("click", () => {
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
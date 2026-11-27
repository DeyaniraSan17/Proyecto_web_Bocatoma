const imagenes = [
  "/static/bocatoma/img/multi_acti.jpg",
  "/static/bocatoma/img/cascada.jpg",
  "/static/bocatoma/img/lancha.jpg"
];

let index = 0;
const img = document.getElementById("imgCarrusel");

document.querySelector(".next").addEventListener("click", () => {
  index = (index + 1) % imagenes.length;
  img.src = imagenes[index];
});

document.querySelector(".prev").addEventListener("click", () => {
  index = (index - 1 + imagenes.length) % imagenes.length;
  img.src = imagenes[index];
});

setInterval(() => {
  index = (index + 1) % imagenes.length;
  img.src = imagenes[index];
}, 4000); 


const imagenesPoza = [
  "/static/bocatoma/img/poza_Azul.jpeg",
  "/static/bocatoma/img/poza_azul.jpg",
  "/static/bocatoma/img/La-Poza-Azul.jpg",
  "/static/bocatoma/img/poza2.jpg"
];

let indexPoza = 0;
const imgPoza = document.getElementById("imgCarruselPoza");

document.querySelector(".next-poza").addEventListener("click", () => {
  indexPoza = (indexPoza + 1) % imagenesPoza.length;
  imgPoza.src = imagenesPoza[indexPoza];
});

document.querySelector(".prev-poza").addEventListener("click", () => {
  indexPoza = (indexPoza - 1 + imagenesPoza.length) % imagenesPoza.length;
  imgPoza.src = imagenesPoza[indexPoza];
});

setInterval(() => {
  indexPoza = (indexPoza + 1) % imagenesPoza.length;
  imgPoza.src = imagenesPoza[indexPoza];
}, 4000);
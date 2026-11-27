const titulo = document.getElementById("titulo-menu");
const Btoma = document.getElementById("inicio");

window.addEventListener("scroll", () => {
  if (window.scrollY > Btoma.offsetHeight - 90) {
    titulo.textContent = "Parque Ecoturistico La Bocatoma";
  } else {
    titulo.textContent = "Parque Ecoturistico";
  }
});


const slides = document.querySelector(".slides");
const images = document.querySelectorAll(".slides img");

const total = images.length - 1;

let index = 0;

setInterval(() => {
  index++;

  slides.style.transition = "transform 0.6s ease-in-out";
  slides.style.transform = `translateX(-${index * 100}%)`;

  if (index === total) {
    setTimeout(() => {
      slides.style.transition = "none";
      index = 0;
      slides.style.transform = "translateX(0)";
    }, 600);
  }

}, 3000);


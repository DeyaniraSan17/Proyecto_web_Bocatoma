  const cards = document.querySelectorAll(".card");
  const overlay = document.getElementById("modalOverlay");
  const modalImg = document.getElementById("modalImg");
  const modalCerrar = document.getElementById("modalCerrar");

  cards.forEach(card => {
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      const rotateX = (-y * 15).toFixed(2);
      const rotateY = (x * 15).toFixed(2);
      card.style.transform = `perspective(600px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.05)`;
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = "perspective(600px) rotateX(0deg) rotateY(0deg) scale(1)";
    });

    const img = card.querySelector("img");
    img.addEventListener("click", () => {
      modalImg.src = img.src;
      overlay.classList.add("activo");
    });
  });

  modalCerrar.addEventListener("click", () => {
    overlay.classList.remove("activo");
  });

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) {
      overlay.classList.remove("activo");
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") overlay.classList.remove("activo");
  });


  modalImg.addEventListener("mousemove", (e) => {
    const rect = modalImg.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    const rotateX = (-y * 10).toFixed(2);
    const rotateY = (x * 10).toFixed(2);
    modalImg.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.03)`;
  });

  modalImg.addEventListener("mouseleave", () => {
    modalImg.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)";
  });

document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("question-list");
  const form = document.getElementById("add-question-form");

  // --- 1. Cargar preguntas existentes ---
  fetch("http://localhost:5000/api/preguntas")
    .then(response => response.json())
    .then(preguntas => {
      preguntas.forEach(p => {
        const card = document.createElement("div");
        card.className = "question-card";

        const title = document.createElement("div");
        title.className = "question-text";
        title.textContent = p.texto;
        card.appendChild(title);

        p.opciones.forEach((op, i) => {
          const opt = document.createElement("div");
          opt.className = "option" + (i === p.correcta ? " correct" : "");
          opt.textContent = `${i + 1}. ${op}`;
          card.appendChild(opt);
        });

        container.appendChild(card);
      });
    })
    .catch(error => {
      console.error("Error al cargar las preguntas:", error);
    });

  // --- 2. Registrar envío del formulario ---
  form.addEventListener("submit", async (event) => {
    event.preventDefault(); // Detener el submit normal

    const pregunta = document.getElementById("question-text").value.trim();
    const respuesta1 = document.getElementById("answer-1").value.trim();
    const respuesta2 = document.getElementById("answer-2").value.trim();
    const respuesta3 = document.getElementById("answer-3").value.trim();
    const correcta = parseInt(document.getElementById("correct-answer").value);

    if (!pregunta || !respuesta1 || !respuesta2 || !respuesta3 || ![1, 2, 3].includes(correcta)) {
      alert("Por favor completa todos los campos correctamente.");
      return;
    }

    const nuevaPregunta = {
      texto: pregunta,
      respuestas: [
        { texto: respuesta1, correcta: correcta === 1 },
        { texto: respuesta2, correcta: correcta === 2 },
        { texto: respuesta3, correcta: correcta === 3 }
      ]
    };

    try {
      const response = await fetch("http://localhost:5000/api/preguntas", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(nuevaPregunta)
      });

      const data = await response.json();

      if (response.ok) {
        alert("Pregunta agregada exitosamente!");
        location.reload(); // Refrescar para ver la nueva pregunta
      } else {
        console.error("Error del servidor:", data);
        alert("Error: " + (data.error || "Error desconocido"));
      }
    } catch (error) {
      console.error("Error en la petición:", error);
      alert("Error de conexión con el servidor.");
    }
  });
});

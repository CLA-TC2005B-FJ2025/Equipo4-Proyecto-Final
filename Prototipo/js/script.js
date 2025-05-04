let imageSrc = '';
const grid = document.getElementById('imageGrid');
let imgWidth, imgHeight;
let preguntasDisponibles = [];
let preguntaActual = null;
let celdaActual = null;
let ticketCount = 0;
let premioOtorgado = false;
let emailUsuario = localStorage.getItem('email') || 'sin-email';

const ticketCounter = document.getElementById('ticketCounter');
const inputContainer = document.querySelector('.input-container');
const userInput = document.getElementById('userInput');
const submitButton = document.getElementById('submitButton');
const questionContainer = document.createElement('div');
questionContainer.className = 'question-container';
document.body.appendChild(questionContainer);

inputContainer.style.display = 'block';
questionContainer.style.display = 'none';
ticketCounter.textContent = `Boletos: ${ticketCount}`;

document.addEventListener("DOMContentLoaded", async function() {
    const nombreImagen = localStorage.getItem("nombreImagen");

    if (!nombreImagen) {
        alert("No se ha encontrado ninguna imagen. Redirigiendo...");
        window.location.href = "iniciar_evento.html";
        return;
    }

    imageSrc = `../../WebServices/static/uploads/${nombreImagen}`;
    
    // Regenera la cuadrícula cada vez que la página se recargue
    await crearCuadricula();
    preguntasDisponibles = await cargarPreguntas();
});

async function cargarPreguntas() {
    try {
        const response = await fetch('http://localhost:5000/api/preguntas');
        if (!response.ok) throw new Error("Error en la respuesta");
        return await response.json();
    } catch (error) {
        console.error("Error cargando preguntas:", error);
        return [];
    }
}

async function cargarGrixelesDesbloqueados() {
    try {
        const response = await fetch('http://localhost:5000/api/grixeles_completos');
        if (!response.ok) throw new Error("Error al obtener grixeles desbloqueados");
        return await response.json();
    } catch (error) {
        console.error("Error al obtener grixeles:", error);
        return [];
    }
}

async function registrarRespuesta(celdaID, respuestaID, esCorrecta) {
    try {
        console.log("Datos a enviar:", {
            email_usuario: emailUsuario,
            grixel_id: celdaID,
            respuesta_id: respuestaID,
            correcta: esCorrecta
        });

        const response = await fetch('http://localhost:5000/api/responde', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email_usuario: emailUsuario,
                grixel_id: celdaID,
                respuesta_id: respuestaID,
                correcta: esCorrecta
            })
        });

        if (response.ok) {
            console.log("Respuesta registrada correctamente");
        } else {
            const errorData = await response.json();
            console.error("Error al registrar respuesta:", errorData);
        }
    } catch (error) {
        console.error("Error en la solicitud de respuesta:", error);
    }
}

async function crearCuadricula() {
    const totalCells = 200;
    const img = new Image();
    img.src = imageSrc;

    img.onload = async () => {
        const imgWidth = img.width;
        const imgHeight = img.height;

        const aspectRatio = imgWidth / imgHeight;
        let cols = Math.round(Math.sqrt(totalCells * aspectRatio));
        let rows = Math.ceil(totalCells / cols);

        while (cols * rows < totalCells) {
            cols++;
            rows = Math.ceil(totalCells / cols);
        }

        // Obtener los grixeles desbloqueados y sus IDs
        const grixelesDesbloqueados = await cargarGrixelesDesbloqueados();
        const idsDesbloqueados = new Set(grixelesDesbloqueados.map(g => parseInt(g.grixel_id)));

        grid.style.display = 'grid';
        grid.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
        grid.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
        grid.style.width = '80vmin';
        grid.style.margin = '20px auto';
        grid.style.backgroundColor = '#000';
        grid.innerHTML = '';  // Limpiar la cuadrícula antes de crearla

        // Crear las celdas de la cuadrícula
        for (let i = 0; i < totalCells; i++) {
            const cell = document.createElement('div');
            const row = Math.floor(i / cols);
            const col = i % cols;

            cell.dataset.id = i;
            cell.dataset.row = row;
            cell.dataset.col = col;
            cell.dataset.cols = cols;
            cell.dataset.rows = rows;

            if (idsDesbloqueados.has(i)) {
                cell.className = 'grid-cell unlocked';
                cell.style.backgroundImage = `url('${imageSrc}')`;
                cell.style.backgroundSize = `${cols * 100}% ${rows * 100}%`;
                cell.style.backgroundPosition = `${(col / (cols - 1)) * 100}% ${(row / (rows - 1)) * 100}%`;
            } else {
                cell.className = 'grid-cell locked';
                cell.addEventListener('click', manejarClickCelda);
            }

            grid.appendChild(cell);
        }
    };
}

async function manejarClickCelda(e) {
    if (preguntasDisponibles.length === 0) {
        preguntasDisponibles = await cargarPreguntas();
        if (preguntasDisponibles.length === 0) {
            alert("No hay preguntas disponibles");
            return;
        }
    }

    const celda = e.target;
    if (!celda.classList.contains('locked')) return;

    celdaActual = celda;
    mostrarPreguntaAleatoria();
}

function mostrarPreguntaAleatoria() {
    const randomIndex = Math.floor(Math.random() * preguntasDisponibles.length);
    preguntaActual = preguntasDisponibles[randomIndex];

    questionContainer.innerHTML = `
        <div class="question">${preguntaActual.texto}</div>
        <div class="options">
            ${preguntaActual.opciones.map((opcion, index) => `
                <button class="option" data-index="${index}">${opcion}</button>
            `).join('')}
        </div>
    `;

    questionContainer.style.display = 'block';

    document.querySelectorAll('.option').forEach(btn => {
        btn.addEventListener('click', manejarSeleccionRespuesta);
    });
}

function manejarSeleccionRespuesta(e) {
    const selectedIndex = parseInt(e.target.dataset.index);
    const esCorrecta = selectedIndex === preguntaActual.correcta;

    if (esCorrecta) {
        desbloquearCelda();
        ticketCount++;
        ticketCounter.textContent = `Boletos: ${ticketCount}`;
        alert("¡Correcto! Celda desbloqueada");
        if (todasLasCeldasDesbloqueadas()) {
            mostrarTodaLaImagen();
            alert("¡Has adivinado la imagen! Te redirigiremos a la página de intentos.");
            window.location.href = 'intentos.html';
        }
    } else {
        alert("Incorrecto. Intenta con otra celda.");
    }

    registrarRespuesta(celdaActual.dataset.id, preguntaActual.id, esCorrecta ? 1 : 0);

    questionContainer.style.display = 'none';
}

function desbloquearCelda() {
    if (!celdaActual) return;

    const col = parseInt(celdaActual.dataset.col);
    const row = parseInt(celdaActual.dataset.row);
    const cols = parseInt(celdaActual.dataset.cols);
    const rows = parseInt(celdaActual.dataset.rows);

    celdaActual.classList.remove('locked');
    celdaActual.classList.add('unlocked');
    celdaActual.style.backgroundImage = `url('${imageSrc}')`;
    celdaActual.style.backgroundSize = `${cols * 100}% ${rows * 100}%`;
    celdaActual.style.backgroundPosition = `${(col / (cols - 1)) * 100}% ${(row / (rows - 1)) * 100}%`;
}

function todasLasCeldasDesbloqueadas() {
    return document.querySelectorAll('.grid-cell.unlocked').length === 200;
}

function mostrarTodaLaImagen() {
    grid.style.backgroundImage = `url('${imageSrc}')`;
    grid.style.backgroundSize = 'cover';
    grid.style.backgroundPosition = 'center';
    grid.style.backgroundRepeat = 'no-repeat';
    grid.style.gridTemplateColumns = '1fr';
    grid.style.gridTemplateRows = '1fr';
    grid.style.width = '100vw';
    grid.style.height = '100vh';
}

let nombreCorrecto = '';

fetch('http://localhost:5000/api/name')
  .then(response => response.json())
  .then(data => {
    if (data.nombre) {
      nombreCorrecto = data.nombre.trim().toLowerCase();
    } else {
      console.error("No se pudo obtener el nombre correcto.");
    }
  })
  .catch(error => console.error('Error al obtener el nombre:', error));

submitButton.addEventListener('click', () => {
    const respuesta = userInput.value.trim().toLowerCase();
    if (respuesta === nombreCorrecto && !premioOtorgado) {
        premioOtorgado = true;
        alert("¡Correcto! Has ganado el Premio A.");
        // Aquí puedes agregar la lógica adicional para otorgar el premio
    } else {
        alert("Respuesta incorrecta o ya has ganado el premio.");
    }
});

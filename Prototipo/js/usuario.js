import apiUrl from '../js/config.js';
document.addEventListener("DOMContentLoaded", function() {
    const historialContainer = document.getElementById('historial');

    // Función para cargar los intentos desde la API
    async function cargarIntentos() {
        try {
            const response = await fetch(`${apiUrl}/api/respuestas`);
            if (!response.ok) {
                throw new Error('Error al obtener los intentos');
            }
            const intentos = await response.json();
            mostrarIntentos(intentos);
        } catch (error) {
            console.error("Error cargando intentos:", error);
            historialContainer.innerHTML = '<p>No se pudieron cargar los intentos. Inténtalo nuevamente.</p>';
        }
    }

    // Función para mostrar los intentos en la página
    function mostrarIntentos(intentos) {
        if (intentos.length === 0) {
            historialContainer.innerHTML = '<p>No hay intentos registrados.</p>';
        } else {
            historialContainer.innerHTML = intentos.map(intento => {
                const fecha = new Date(intento.fecha_respuesta).toLocaleString();
                return `
                    <div class="intento">
                        <p><strong>Celda:</strong> ${intento.grixel_id}</p>
                        <p><strong>Respuesta:</strong> ${intento.correcta ? 'Correcta' : 'Incorrecta'}</p>
                        <p><strong>Usuario:</strong> ${intento.email_usuario}</p>
                        <p><strong>Fecha:</strong> ${fecha}</p>
                    </div>
                `;
            }).join('');
        }
    }

    // Cargar los intentos cuando la página se cargue
    cargarIntentos();
});

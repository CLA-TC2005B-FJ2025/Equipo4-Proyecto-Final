import apiUrl from './config.js';
document.getElementById('start-event-btn').addEventListener('click', async function() {
    try {
        // Primero, borrar el contenido de la tabla "responde"
        const borrarRespondeResponse = await fetch('${apiUrl}/api/borrar_responde', {
          method: 'DELETE'
        });
  
        if (!borrarRespondeResponse.ok) {
            throw new Error("Error al borrar los datos de la tabla responde.");
        }
  
        // Hacer una solicitud al backend para obtener el nombre de la última imagen añadida
        const response = await fetch('${apiUrl}/api/ultima-imagen');
        const data = await response.json();
  
        if (response.ok && data.nombre) {
            // Guardar el nombre de la imagen en localStorage
            localStorage.setItem('nombreImagen', data.nombre);
            document.getElementById('start-message').textContent = `Evento iniciado con la imagen: ${data.nombre}`;
            alert("¡Evento iniciado con éxito!.");
        } else {
            document.getElementById('start-message').textContent = "No se encontró ninguna imagen en la base de datos.";
        }
    } catch (error) {
        console.error('Error al iniciar el evento:', error);
        document.getElementById('start-message').textContent = 'Hubo un error al iniciar el evento.';
    }
  });
  

import apiUrl from './config.js';
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('signinForm');  // Usamos el ID del formulario

  form.addEventListener('submit', async (e) => {
      e.preventDefault();  // Previene el comportamiento por defecto del formulario

      // Obtener los valores del formulario
      const username = form.username.value.trim();
      const email = form.email.value.trim();
      const password = form.password.value;
      const confirmPassword = form['confirm-password'].value;

      // Verificar si las contraseñas coinciden
      if (password !== confirmPassword) {
          alert("Las contraseñas no coinciden.");
          return;
      }

      // Mostrar los datos que se están enviando
      console.log('Datos a enviar:', { username, email, password });

      try {
          const res = await fetch('${apiUrl}/api/signup', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ username, email, password })
          });

          // Mostrar la respuesta del servidor
          const data = await res.json();
          console.log('Respuesta del servidor:', data);

          if (res.ok) {
              alert('¡Sign up exitoso! Ahora puedes iniciar sesión.');
              window.location.href = '../../index.html';  // Redirigir al login
          } else {
              alert(data.error || 'Error al registrarse');
          }
      } catch (err) {
          console.error(err);
          alert('No se pudo conectar al servidor');
      }
  });
});

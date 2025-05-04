import apiUrl from '../js/config.js';
// Función de manejo del login con Google
window.handleGoogleLogin = function (response) {
    console.log("ID Token recibido:", response.credential);
  
    // Guardar el token en localStorage (opcional)
    localStorage.setItem('google_token', response.credential);
  
    // Redirigir después del login
    window.location.href = 'Prototipo/html/indexGura.html';
  };
  
  document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
  
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
  
        const email = form.email.value.trim();
        const password = form.password.value;
  
        try {
          const res = await fetch(`${apiUrl}/api/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
          });
  
          const data = await res.json();
  
          if (res.ok) {
            alert('¡Login exitoso!');
  
            // Guardar email en localStorage
            localStorage.setItem('email', email);
  
            if (data.is_admin) {
              window.location.href = 'Prototipo/html/admin.html';
            } else {
              window.location.href = 'Prototipo/html/indexGura.html';
            }
          } else {
            alert(data.error || 'Error en el inicio de sesión');
          }
  
        } catch (err) {
          console.error(err);
          alert('No se pudo conectar al servidor');
        }
      });
    }
  
    // Botón de Facebook (sin funcionalidad real aún)
    const fbBtn = document.getElementById('facebookLogin');
    if (fbBtn) {
      fbBtn.addEventListener('click', () => {
        alert('Login con Facebook aún no está disponible.');
      });
    }
  });
  
  // Inicializar e insertar botón de Google
  window.onload = function () {
    google.accounts.id.initialize({
      client_id: '1002362330379-q4qf1nj4r05rclrgkpq0bqlrafq6ljf3.apps.googleusercontent.com',
      callback: handleGoogleLogin
    });
  
    google.accounts.id.renderButton(
      document.getElementById('googleSignInDiv'),
      { theme: 'outline', size: 'large' }
    );
  };
  

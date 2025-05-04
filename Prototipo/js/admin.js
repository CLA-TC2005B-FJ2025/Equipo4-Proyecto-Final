document.addEventListener('DOMContentLoaded', function() {
    const galleryBtn = document.getElementById('gallery-btn');
    const usersBtn = document.getElementById('users-btn');
    const eventBtn = document.getElementById('event-btn');
    const questionsBtn = document.getElementById('questions-btn');
    const adminContent = document.getElementById('admin-content');
    
    galleryBtn.addEventListener('click', function() {
        adminContent.innerHTML = `
            <h2>Galería - Admin</h2>
            <div class="admin-section">
                <h3>Subir imagen</h3>
                <input type="file" id="image-upload">
                <button class="btn-action">Subir</button>
            </div>
        `;
    });
    
    usersBtn.addEventListener('click', function() {
        adminContent.innerHTML = `
            <h2>Usuarios - Admin</h2>
            <div class="admin-section">
                <h3>Roles</h3>
                <button class="btn-action">Administrar</button>
            </div>
        `;
    });
    
    eventBtn.addEventListener('click', function() {
        adminContent.innerHTML = `
            <h2>Iniciar evento</h2>
            <div class="admin-section">
                <button class="btn-action">Comenzar nuevo evento</button>
            </div>
        `;
    });
    
    questionsBtn.addEventListener('click', function() {
        adminContent.innerHTML = `
            <h2>Banco de preguntas</h2>
            <div class="admin-section">
                <button class="btn-action">Agregar pregunta</button>
                <button class="btn-action">Editar preguntas</button>
            </div>
        `;
    });
    document.addEventListener("DOMContentLoaded", () => {
        const loginForm = document.getElementById("loginForm");
      
        loginForm.addEventListener("submit", (e) => {
          e.preventDefault(); 
      
          const email = document.getElementById("email").value.trim();
          const password = document.getElementById("password").value;
      
          if (password === "contraaseña") {
            if (email === "admin@gmail.com") {
              window.location.href = "admin.html";
            } else if (email === "usuario@gmail.com") {
              window.location.href = "indexGura.html";
            } else {
              alert("Correo no reconocido.");
            }
          } else {
            alert("Contraseña incorrecta.");
          }
        });
      });
      


    galleryBtn.click();
});
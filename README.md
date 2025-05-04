# CRUD_server_Equipo4

Este es el sistema de CRUD (create, read, delete, update) del equipo 4 para el proyecto con el socio formador Lienzo. El equipo esta conformado por: 

- Fernando Sigala Rascón A01563650
- Jesús Alexander Herrera Acevedo A01563465
- Nadia Susana Soto Juarez A01563655
- Mauricio Balbuena Martinez A01563331


## Prerequisitos

Antes de comenzar, asegúrate de tener:

- *GitHub Codespaces* habilitado.
- *Docker* ejecutándose en tu Codespace.
- *Python 3* instalado.
- *pymssql* instalado en tu entorno Python.
- Todas las librerias pedidas en el python.

### Iniciar la instancia de SQL Server en Docker

Para iniciar una instancia de *SQL Server* en un contenedor Docker, ejecuta el siguiente comando en la terminal de tu *GitHub Codespace*:

sh
docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=YourPassword123!' \
   -p 1433:1433 --name sqlserver -d mcr.microsoft.com/mssql/server:2022-latest


### Instalar sqlcmd
sh
sudo apt update
sudo apt install mssql-tools unixodbc-dev
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
source ~/.bashrc

### Iniciamos la base de datos 
sh
sqlcmd -S localhost -U SA -P "YourPassword123!" -i "LienzoDatabase.sql"


### Abra *otra* terminal (no cierre la terminal que está ejecutando el servidor), y ejecute el código de WEBservices

En el código "configuración.js" remplazar el url con el que se genera por el webservice en el puerto 5000, es importarte borrar el slash final para que no haya interferencia en el código.

Despliega la página web con github pages y esta listo para probar (con excepción del juego, este por el momento solo se encuentra localmente debido a que github codespaces no guarda las imagenes subidas 
en dicha iteración).

# Plan para migrar a Docker

El entorno de buildpacks de Render ha demostrado ser inconsistente para ejecutar Selenium. Para resolver esto, migraremos la aplicación a un entorno de Docker, lo que nos da control total sobre las dependencias del sistema.

## Pasos a seguir:

1.  **Crear `Dockerfile`**:
    -   Definir un archivo `Dockerfile` que instale una versión específica de Python, Google Chrome y el `chromedriver` compatible.
    -   Copiar el código de la aplicación y las dependencias.
    -   Configurar el comando de inicio (Gunicorn).

2.  **Actualizar `lenovo_checker2.py`**:
    -   Revertir el script para que vuelva a utilizar el objeto `ChromeService` de Selenium, apuntando a las rutas fijas que definiremos en el `Dockerfile`.

3.  **Modificar `render.yaml`**:
    -   Cambiar el tipo de entorno de `python` a `docker`.
    -   Eliminar la sección `buildPacks`.
    -   Asegurarse de que las variables de entorno (`GOOGLE_CHROME_BIN` y `CHROMEDRIVER_PATH`) apunten a las rutas correctas dentro del contenedor.

4.  **Actualizar `requirements.txt`**:
    -   Fijar la versión de `selenium` para garantizar la estabilidad entre despliegues.

5.  **Desplegar**:
    -   Hacer commit de los archivos nuevos y modificados (`Dockerfile`, `render.yaml`, `lenovo_checker2.py`, `requirements.txt`).
    -   Hacer `git push` para que Render construya la imagen de Docker y despliegue el servicio.

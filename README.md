# ***TFG - Urban Street Mapping Transfer***

+ ## ***Autor:***
    + Mario Hurtado Ubierna
+ ## ***Tutores:***
    + Virginia Ahedo García
    + Jesús Manuel Maudes Raedo

---

## **Descripción:**
Urban Street Mapping es un proyecto que pretende utilizar la aplicación OpenStreetMap para extraer tanto la categoría comercial de los distintos establecimientos de la ciudad de Burgos, como los distintos Puntos de Interés (parques, monumentos, iglesias, parkings, etc.). Para recoger esta información (así como la geolocalización de los distintos puntos), se utilizará la API de OpenStreetMap. Posteriormente, la información obtenida se guardará en una base de datos convenientemente estructurada. La explotación de los datos consistirá en la creación de las redes de interacción entre los distintos elementos (locales comerciales clasificados por categorías y Puntos de Interés) en base a una (o más) de las técnicas de disponibles en la literatura científica para tal fin. El output esperado será de una herramienta que nos permita realizar recomendaciones de localización para futuros negocios teniendo en cuenta el aprendizaje obtenido de las redes de interacción.

---

## **Uso de la aplicación**

[página web de la aplicación](https://usmt-68ffcbc61e83.herokuapp.com/home)

### **Uso desde Docker**

La aplicación puede utilizarse utilizando Docker. Primero, dado que se requiere de una base de datos cargada tendremos que descargar el volcado de la base de datos `neo4j.dump` desde [esta dirección](https://universidaddeburgos-my.sharepoint.com/:f:/g/personal/mhu1001_alu_ubu_es/Evm-45Fq9y1Ps-F3_PGd5KsBNR3G0JAR2-t1IrXBDm2BEQ?e=A0bB0w). Situaremos este fichero dentro de `/src`. Una vez hecho esto podemos lanzar la aplicación utilizando Docker desde este directorio.

- Construir contenedores de docker
```bash
docker compose build
```
- Lanzar contenedores
```bash
docker compose up
```

Una vez lanzados los contenedores la aplicación podrá accederse desde esta dirección http://127.0.0.1:5000/home.

Cuando queramos detener la ejecución pulsarmeos `Ctrl + C`. Para borrar los contendores introduciremos:

```bash
docker compose down
```
## **Variables de entorno**

La aplicación requiere de la definición de una serie de variables de entorno. Esto se puede hacer creando un fichero `.env` dentro de la carpeta `/src`. Las empleadas por Docker están definidas en 'src/docker-compose.yml'.

Contamos con las siguientes variables de entorno:

  - FLASK_APP: Nombre de la aplicación de Flask a lanzar.
  - FLASK_DEBUG: Booleano por si se quiere lanzar la aplición en modo Debug.
  - FLASK_RUN_PORT: Número de puerto en el que lanzar la aplicación.
  - FLASK_RUN_HOST: Dirección IP del host sobre el que lanzar la aplicación web.
  - NEO4J_URI: URI de acceso a la base de datos de Neo4j.
  - NEO4J_USER: Usuario de acceso a la base de datos de Neo4j.
  - NEO4J_PASSWORD: Contraseña de acceso a la base de datos Neo4j.
  - JWT_SECRET_KEY: Clave para JWT.
  - DEFAULT_USER: Usuario por defecto de la aplicación.
  - DEFAULT_PASSWORD: Contraseña del usuario por defecto de la aplicación.
  - SECRET_KEY: Clave secreta de Flask.

## Requisitos de la aplicación

Las dependecias de Python para lanzar la aplicación se encuentran dentro del fichero `requirements.txt`. Para instalarlas introduciremos:

```bash
pip install -r requirements.txt
```

## Lanzar la aplicación con Python

Para lanzar la aplicación si queremos utilizarla sin Docker bastará con ejecutar `flask run` desde el directorio `/src`. Para poder hacer esto previamente tendremos que:

- Disponer de una base de datos Neo4j cargada con el volcado.
- Disponer de Python 3.10.
- Instalar las dependencias de la aplicación.
- Definir las variables de entorno de la aplicación.



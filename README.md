---

# 🚀 ReverseTunnel v1.0: Conecta tu API de Ollama de forma segura y sencilla

¡Estamos emocionados de anunciar el lanzamiento de **ReverseTunnel v1.0**! 🎉  
Esta herramienta te permite exponer de manera segura y eficiente la API de **Ollama** desde un servidor remoto (Linux) a tu máquina local, o incluso a entornos como **Google Colab** o cualquier otro que admita conexiones SSH. ¡Y lo mejor de todo? ¡Es completamente **gratis**! 🆓

---

## 🔥 ¿Qué hace ReverseTunnel?

**ReverseTunnel** es una herramienta diseñada para simplificar la conexión entre tu servidor remoto y tu entorno local. Con esta herramienta, puedes:

- **Exponer la API de Ollama** desde un servidor Linux (por ejemplo, `http://localhost:11434`) a tu máquina local.
- Crear **túneles inversos** para acceder a servicios internos de forma segura.
- Funcionar en entornos como **Google Colab**, **Jupyter Notebooks**, o cualquier otro que admita conexiones SSH.
- Integrarse con herramientas como **Serveo** o **Ngrok** para crear túneles de manera rápida y sencilla.

---

## 🛠️ Características principales

- **Configuración sencilla**: Interfaz interactiva para configurar los parámetros del túnel (host, puerto, usuario, contraseña, etc.).
- **Reconexión automática**: Si la conexión falla, ReverseTunnel intentará reconectarse automáticamente.
- **Persistencia de configuración**: Guarda tus configuraciones para no tener que ingresarlas cada vez que uses la herramienta.
- **Compatibilidad multiplataforma**: Funciona en cualquier entorno que admita Python y conexiones SSH.

---

## 📦 ¿Cómo funciona?

1. **Configura el túnel**: Ingresa los detalles de tu servidor remoto (host, puerto, usuario, contraseña) y los puertos locales y remotos.
2. **Establece la conexión**: ReverseTunnel creará un túnel inverso entre tu servidor y tu máquina local.
3. **Accede a la API**: Una vez establecido el túnel, podrás acceder a la API de Ollama desde `localhost`.

---

## 🚀 Instalación y uso

1. Clona el repositorio:
   ```bash
   git clone https://github.com/HirCoir/ReverseTunnel.git
   cd ReverseTunnel
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta la herramienta:
   ```bash
   python ReverseTunnel.py
   ```

4. Sigue las instrucciones en pantalla para configurar y activar el túnel.

---

## 🌟 ¿Por qué usar ReverseTunnel?

- **Fácil de usar**: No necesitas ser un experto en redes para configurar y usar ReverseTunnel.
- **Seguro**: Utiliza conexiones SSH para garantizar la seguridad de tus datos.
- **Versátil**: Compatible con múltiples entornos y herramientas de tunneling.
- **Gratuito**: ¡No tienes que pagar nada para usar esta herramienta!

---

## 📂 Repositorio y contribuciones

El código fuente de **ReverseTunnel** está disponible en GitHub. ¡Siéntete libre de contribuir, reportar issues o sugerir mejoras!  
🔗 [https://github.com/HirCoir/ReverseTunnel](https://github.com/HirCoir/ReverseTunnel)

---

## 📜 Notas de la versión (v1.0)

- **Lanzamiento inicial**: Primera versión estable de ReverseTunnel.
- **Funcionalidades clave**: Configuración interactiva, reconexión automática y persistencia de configuraciones.
- **Compatibilidad**: Funciona con Ollama, Serveo, Ngrok y otros servicios similares.

---

## 📢 ¡Pruébalo ahora!

No esperes más para simplificar tus conexiones remotas. Descarga **ReverseTunnel** y comienza a disfrutar de una forma más sencilla y segura de acceder a tus APIs y servicios internos.

¡Tu feedback es importante! Si tienes alguna pregunta, sugerencia o problema, no dudes en abrir un issue en el repositorio. 😊

---

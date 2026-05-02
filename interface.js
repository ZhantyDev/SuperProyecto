/**
 * Crea e inyecta la interfaz de usuario para SentimentStream.
 */
function initInterface() {
    // 0. Cargar Storage API
    const storageScript = document.createElement('script');
    storageScript.src = 'storage_api.js';
    document.head.appendChild(storageScript);

    // 1. Cargar CSS
    const stylesLink = document.createElement('link');
    stylesLink.rel = 'stylesheet';
    stylesLink.href = 'interface_styles.css';
    document.head.appendChild(stylesLink);

    // 2. Generar Estructura HTML
    const uiContainer = document.createElement('div');
    uiContainer.className = 'ui-container';

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'comment-input';
    input.placeholder = 'Dime tu comentario';

    const button = document.createElement('button');
    button.className = 'submit-btn';
    button.textContent = 'Enviar';

    const historialBtn = document.createElement('button');
    historialBtn.className = 'historial-btn';
    historialBtn.textContent = '📊 Historial';

    const buttonGroup = document.createElement('div');
    buttonGroup.className = 'button-group';
    buttonGroup.appendChild(button);
    buttonGroup.appendChild(historialBtn);

    uiContainer.appendChild(input);
    uiContainer.appendChild(buttonGroup);

    const floatingResult = document.createElement('div');
    floatingResult.className = 'floating-result';

    // Crear contenedor para historial
    const historialContainer = document.createElement('div');
    historialContainer.className = 'historial-container';

    document.body.appendChild(uiContainer);
    document.body.appendChild(floatingResult);
    document.body.appendChild(historialContainer);

    // 3. Lógica de Interacción
    // Definimos la función ASYNC directamente aquí
    async function procesarComentario() {
        const comentario = input.value.trim();

        if (!comentario) return;

        // Feedback visual de carga
        floatingResult.textContent = "...";
        floatingResult.classList.add('show');

        try {
            console.log("Enviando a la API:", comentario); // Esto aparecerá en la consola del navegador

            const response = await fetch('http://localhost:5005/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: comentario })
            });

            if (!response.ok) throw new Error('Error en la comunicación con la API');

            const data = await response.json();
            const resultado = data.sentiment;

            // Actualizar el cuadro flotante con el resultado
            floatingResult.textContent = resultado;

            // Colores según sentimiento
            let glowColor = 'rgba(135, 206, 235, 0.8)'; 
            if (resultado === 'Positivo') glowColor = 'rgba(74, 222, 128, 0.8)';
            else if (resultado === 'Negativo') glowColor = 'rgba(248, 113, 113, 0.8)';

            floatingResult.style.textShadow = `0 0 25px rgba(0, 0, 0, 0.9), 0 0 15px ${glowColor}`;

            // Reiniciar animación
            floatingResult.classList.remove('show');
            void floatingResult.offsetWidth; // Force reflow
            floatingResult.classList.add('show');

            // Limpiar input
            input.value = '';

        } catch (error) {
            console.error("Hubo un error:", error);
            floatingResult.textContent = "Error API";
            floatingResult.style.color = "#ff4d4d";
        }
    }

    // Asignar el evento a la función correcta
    button.addEventListener('click', procesarComentario);

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            procesarComentario();
        }
    });

    // Agregar evento para mostrar/ocultar historial
    historialBtn.addEventListener('click', async () => {
        if (historialContainer.style.display === 'none') {
            // Cargar historial desde MongoDB
            try {
                historialBtn.textContent = '⏳ Cargando...';
                historialBtn.disabled = true;

                const historial = await storage.obtenerHistorial(20);

                // Limpiar contenedor
                historialContainer.innerHTML = '';

                // Crear título
                const titulo = document.createElement('h3');
                titulo.textContent = 'Historial de Análisis';
                historialContainer.appendChild(titulo);

                // Mostrar últimas predicciones
                if (historial.length > 0) {
                    const listDiv = document.createElement('div');
                    listDiv.className = 'historial-list';

                    historial.forEach(pred => {
                        const item = document.createElement('div');
                        item.className = 'historial-item';
                        const fecha = new Date(pred.timestamp).toLocaleString('es-ES');
                        const sentimiento = pred.prediccion || pred.intencion_predicha || 'desconocido';

                        item.innerHTML = `
                            <p><strong>Texto:</strong> "${pred.texto}"</p>
                            <p><strong>Sentimiento:</strong> <span class="sentiment-${sentimiento.toLowerCase()}">${sentimiento}</span></p>
                            <p><strong>Fecha:</strong> ${fecha}</p>
                        `;
                        listDiv.appendChild(item);
                    });

                    historialContainer.appendChild(listDiv);
                } else {
                    const empty = document.createElement('p');
                    empty.className = 'historial-empty';
                    empty.textContent = 'No hay predicciones almacenadas aún.';
                    historialContainer.appendChild(empty);
                }

                historialContainer.style.display = 'block';
                historialBtn.textContent = 'Cerrar';
            } catch (error) {
                console.error('Error cargando historial:', error);
                historialContainer.innerHTML = '<p style="color: red;">Error al cargar el historial</p>';
                historialContainer.style.display = 'block';
            } finally {
                historialBtn.disabled = false;
            }
        } else {
            // Ocultar historial
            historialContainer.style.display = 'none';
            historialBtn.textContent = 'Historial';
        }
    });
}

// Inicializar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initInterface);
} else {
    initInterface();
}
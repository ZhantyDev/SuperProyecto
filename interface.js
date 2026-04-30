/**
 * Crea e inyecta la interfaz de usuario para SentimentStream.
 * Este script es autónomo y genera la estructura HTML, CSS y la lógica de interacción.
 */
function initInterface() {
    // 1. Inyectar CSS Dinámico
    const styles = document.createElement('style');
    styles.textContent = `
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-image: url('image_0.png');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-color: #050510; /* Fallback espacial oscuro */
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .ui-container {
            position: absolute;
            bottom: 1rem;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            flex-direction: column;
            align-items: center;
            z-index: 10;
        }

        .comment-input {
            background-color: transparent;
            border: 1px solid white;
            color: white;
            padding: 15px 25px;
            font-size: 1.2rem;
            border-radius: 4px;
            width: 350px;
            text-align: center;
            outline: none;
            transition: box-shadow 0.3s ease, border-color 0.3s ease, background-color 0.3s ease;
            backdrop-filter: blur(2px); /* Desenfoca ligeramente el fondo tras el input */
        }

        .comment-input::placeholder {
            color: rgba(255, 255, 255, 0.7);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 1rem;
        }

        .comment-input:focus {
            border-color: #87CEEB;
            box-shadow: 0 0 15px rgba(135, 206, 235, 0.4);
            background-color: rgba(0, 0, 0, 0.2);
        }

        .submit-btn {
            margin-top: 25px;
            background-color: rgba(0, 0, 0, 0.4);
            border: 1px solid white;
            color: white;
            padding: 12px 40px;
            font-size: 1rem;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 2px;
            backdrop-filter: blur(2px);
        }

        .submit-btn:hover {
            background-color: rgba(255, 255, 255, 0.15);
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }

        .submit-btn:active {
            transform: translateY(1px);
        }

        .floating-result {
            position: absolute;
            top: 15%; /* Ajuste para sobreponerse a la curvatura de la Tierra */
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 3.5rem;
            font-weight: bold;
            text-shadow: 0 0 25px rgba(0, 0, 0, 0.9), 0 0 15px rgba(135, 206, 235, 0.8);
            opacity: 0;
            pointer-events: none;
            z-index: 5;
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        
        /* Animación para la flotación y desvanecimiento del resultado */
        .floating-result.show {
            animation: floatReveal 3s ease forwards;
        }

        @keyframes floatReveal {
            0% { transform: translate(-50%, -40%); opacity: 0; filter: blur(10px); }
            15% { opacity: 1; filter: blur(0px); transform: translate(-50%, -50%); }
            80% { opacity: 1; filter: blur(0px); transform: translate(-50%, -60%); }
            100% { transform: translate(-50%, -70%); opacity: 0; filter: blur(5px); }
        }
    `;
    document.head.appendChild(styles);

    // 2. Generar Estructura HTML
    const uiContainer = document.createElement('div');
    uiContainer.className = 'ui-container';

    // Elemento Input
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'comment-input';
    input.placeholder = 'Dime tu comentario';

    // Elemento Botón
    const button = document.createElement('button');
    button.className = 'submit-btn';
    button.textContent = 'Enviar';

    uiContainer.appendChild(input);
    uiContainer.appendChild(button);

    // Elemento de Resultado Flotante
    const floatingResult = document.createElement('div');
    floatingResult.className = 'floating-result';

    // Anexar elementos al DOM
    document.body.appendChild(uiContainer);
    document.body.appendChild(floatingResult);

    // 3. Lógica de Interacción
    button.addEventListener('click', procesarComentario);

    // Soportar envío al presionar Enter en el input
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            procesarComentario();
        }
    });

    function procesarComentario() {
        const comentario = input.value.trim();

        // No procesar si no han escrito nada (opcional, pero útil)
        if (!comentario) return;

        // Generar respuesta aleatoria según los requisitos
        const opciones = ['Positivo', 'Negativo', 'Neutral'];
        const resultadoAleatorio = opciones[Math.floor(Math.random() * opciones.length)];

        // Actualizar el texto del cuadro flotante
        floatingResult.textContent = resultadoAleatorio;

        // Mejorar la estética del resultado con colores dependientes del sentimiento
        let glowColor = 'rgba(135, 206, 235, 0.8)'; // Azul claro por defecto para Neutral
        let textColor = '#ffffff';

        if (resultadoAleatorio === 'Positivo') {
            glowColor = 'rgba(74, 222, 128, 0.8)'; // Brillo verde
            textColor = '#e0ffe0';
        } else if (resultadoAleatorio === 'Negativo') {
            glowColor = 'rgba(248, 113, 113, 0.8)'; // Brillo rojo
            textColor = '#ffe0e0';
        }

        floatingResult.style.color = textColor;
        floatingResult.style.textShadow = `0 0 25px rgba(0, 0, 0, 0.9), 0 0 15px ${glowColor}`;

        // Reiniciar la animación forzando un reflow
        floatingResult.classList.remove('show');
        void floatingResult.offsetWidth;
        floatingResult.classList.add('show');

        // Limpiar el campo de texto inmediatamente, reestableciendo el placeholder
        input.value = '';
    }
}

// Inicializar cuando el DOM cargue
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initInterface);
} else {
    initInterface();
}

/**
 * Storage API
 * 
 * Módulo para gestionar el almacenamiento de predicciones en MongoDB
 * Se comunica con el backend (Flask API) que se encarga de la persistencia
 */

class StorageAPI {
    constructor(apiUrl = 'http://localhost:5005') {
        this.apiUrl = apiUrl;
    }

    /**
     * Almacena una predicción en MongoDB a través del API
     * 
     * @param {Object} prediccionData - Datos de la predicción
     * @param {string} prediccionData.texto - Texto original analizado
     * @param {string} prediccionData.sentiment - Sentimiento predicho (positivo/negativo/neutral)
     * @param {number} prediccionData.confianza - Nivel de confianza del modelo (0-1)
     * @returns {Promise<Object>} Respuesta del servidor
     */
    async almacenarPrediccion(prediccionData) {
        try {
            const response = await fetch(`${this.apiUrl}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: prediccionData.texto,
                    sentiment: prediccionData.sentiment,
                    confianza: prediccionData.confianza || null,
                    timestamp: new Date().toISOString()
                })
            });

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('✓ Predicción almacenada exitosamente:', data);
            return data;

        } catch (error) {
            console.error('✗ Error al almacenar predicción:', error);
            throw error;
        }
    }

    /**
     * Obtiene el historial de predicciones almacenadas
     * 
     * @param {number} limite - Número máximo de registros a retornar
     * @returns {Promise<Array>} Lista de predicciones almacenadas
     */
    async obtenerHistorial(limite = 50) {
        try {
            const response = await fetch(`${this.apiUrl}/historial?limite=${limite}`);

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            // El backend puede devolver directamente un array de predicciones
            if (Array.isArray(data)) {
                console.log(`✓ Historial obtenido: ${data.length} registros`);
                return data;
            }

            console.log(`✓ Historial obtenido: ${Array.isArray(data.predicciones) ? data.predicciones.length : 0} registros`);
            return data.predicciones || [];

        } catch (error) {
            console.error('✗ Error al obtener historial:', error);
            return [];
        }
    }

    /**
     * Obtiene estadísticas de sentimientos analizados
     * 
     * @returns {Promise<Array>} Estadísticas por sentimiento
     */
    async obtenerEstadisticas() {
        try {
            const response = await fetch(`${this.apiUrl}/stats`);

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('✓ Estadísticas obtenidas:', data);
            return data.estadisticas || [];

        } catch (error) {
            console.error('✗ Error al obtener estadísticas:', error);
            return [];
        }
    }

    /**
     * Obtiene el resumen estadístico completo
     * 
     * @returns {Promise<Object>} Resumen con historial y estadísticas
     */
    async obtenerResumen() {
        try {
            const historial = await this.obtenerHistorial(10);

            return {
                historialReciente: historial,
                estadisticas: [],
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            console.error('✗ Error al obtener resumen:', error);
            return null;
        }
    }

    /**
     * Formatea una predicción para mostrar en la interfaz
     * 
     * @param {Object} prediccion - Objeto de predicción de MongoDB
     * @returns {Object} Predicción formateada
     */
    formatearPrediccion(prediccion) {
        return {
            texto: prediccion.texto || '',
            sentimiento: prediccion.prediccion || prediccion.intencion_predicha || '',
            fecha: new Date(prediccion.timestamp).toLocaleString('es-ES'),
            confianza: prediccion.confianza || 'N/A'
        };
    }

    /**
     * Calcula estadísticas resumidas
     * 
     * @param {Array} estadisticas - Array de estadísticas desde el API
     * @returns {Object} Resumen estadístico
     */
    calcularResumen(estadisticas) {
        const resumen = {
            totalAnalizado: 0,
            positivos: 0,
            negativos: 0,
            neutrales: 0,
            distribucion: {}
        };

        estadisticas.forEach(stat => {
            const sentimiento = stat._id || 'desconocido';
            const total = stat.total || 0;

            resumen.totalAnalizado += total;
            resumen.distribucion[sentimiento] = total;

            // Mapear nombres
            if (sentimiento.toLowerCase() === 'positivo') {
                resumen.positivos = total;
            } else if (sentimiento.toLowerCase() === 'negativo') {
                resumen.negativos = total;
            } else if (sentimiento.toLowerCase() === 'neutral') {
                resumen.neutrales = total;
            }
        });

        return resumen;
    }
}

// Crear instancia global del Storage API
const storage = new StorageAPI();

// Exportar para uso en módulos (si se usa con bundler)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StorageAPI;
}

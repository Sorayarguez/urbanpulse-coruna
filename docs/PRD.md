# PRD - UrbanPulse Coruna

## 1. Objetivo y alcance

### 1.1 Objetivo del producto
UrbanPulse Coruna es una plataforma FIWARE NGSI-LD de monitorizacion ambiental urbana para A Coruna que correlaciona en tiempo real contaminacion atmosferica, ruido urbano y flujos de trafico. El producto actua como gemelo digital ambiental de la ciudad, combinando observacion IoT, analitica historica, prediccion ML y explicacion automatica en espanol con LLM local.

### 1.2 Problema que resuelve
La gestion urbana suele tratar trafico y calidad ambiental por separado. UrbanPulse Coruna unifica ambos dominios para:
- Detectar picos de contaminacion asociados a eventos de movilidad.
- Anticipar escenarios de impacto 6/12/24 horas.
- Explicar causas probables y evolucion esperada en lenguaje natural.
- Facilitar decisiones de gestion municipal y recomendaciones ciudadanas.

### 1.3 Alcance funcional
El alcance incluye los tres ejes fusionados del proyecto:
- GreenRoute: recomendaciones de ruta saludable para reducir exposicion.
- UrbanPulse: dashboard de correlacion trafico-contaminacion como nucleo operativo.
- EcoZones: soporte a activacion dinamica de zonas de bajas emisiones (ZBE).

### 1.4 Alcance geografico y datos
- Ambito: municipio de A Coruna.
- Centro operacional de mapa: 43.3713, -8.4194.
- Red inicial de sensores: sensor-001 a sensor-006 en Avda. de Finisterre, Ronda de Outeiro, Cuatro Caminos, Paseo Maritimo, Torre Hercules y Monte San Pedro.

### 1.5 Fuera de alcance
- Integraciones con APIs de pago externas para LLM.
- Modelado de entidades NGSIv2.
- Despliegue multi-ciudad en esta fase.

## 2. Usuarios objetivo

### 2.1 Gestores municipales
Perfil: equipos de movilidad, medio ambiente y planificacion urbana.
Necesidades:
- Visualizar zonas con impacto ambiental persistente.
- Simular activacion de ZBE y estimar reduccion de contaminantes.
- Recibir alertas operativas cuando se superan umbrales criticos.
Decisiones clave:
- Activar/desactivar medidas de restriccion por zona y franja horaria.
- Priorizar actuaciones segun impacto y tendencia.

### 2.2 Ciudadania
Perfil: residentes y personas que se desplazan por la ciudad.
Necesidades:
- Conocer estado ambiental de su barrio en una interfaz simple.
- Recibir recomendaciones diarias y rutas mas saludables.
- Entender en lenguaje claro por que empeora o mejora el aire.
Decisiones clave:
- Elegir ruta peatonal/ciclista segun exposicion esperada.
- Ajustar horarios de actividad al riesgo ambiental.

### 2.3 Investigadores
Perfil: universidades, centros tecnologicos y analistas de datos urbanos.
Necesidades:
- Explorar series historicas y correlaciones trafico-contaminacion.
- Consultar entidades NGSI-LD para analisis reproducible.
- Contrastar predicciones con observaciones reales.
Decisiones clave:
- Definir hipotesis y validar impacto de eventos de movilidad.
- Evaluar calidad de modelos de prediccion en distintos horizontes.

## 3. Funcionalidades principales

### F1. Mapa de calor ambiental en tiempo real
Descripcion:
- Mapa Leaflet + OSM centrado en A Coruna.
- Capas activables para AQI, ruido y trafico.
- Heatmap dinamico con actualizacion cada 30 segundos.
- Marcadores de sensores con popup de metricas actuales y tendencia ultima hora.
- Escala de color por indice AQI europeo (verde, amarillo, naranja, rojo, violeta).

Valor para usuarios:
- Gestor municipal: deteccion inmediata de hotspots.
- Ciudadania: comprension visual rapida del riesgo por zona.

### F2. Dashboard de correlacion trafico-contaminacion
Descripcion:
- Graficas ChartJS con ejes duales: trafico (veh/h) y NO2/PM2.5 (ug/m3).
- Deteccion de eventos: atasco, obra y evento masivo por umbrales.
- Integracion con Grafana embebido para analisis historico sobre CrateDB.

Valor para usuarios:
- Gestor municipal: contexto operativo para decisiones de regulacion.
- Investigador: analisis temporal y comparativo con mayor profundidad.

### F3. Prediccion ML 6/12/24h con TrafficEnvironmentImpactForecast
Descripcion:
- Pipeline de prediccion con Random Forest (scikit-learn) y LSTM (TensorFlow).
- Entrenamiento con historico simulado de 30 dias.
- Features: hora, dia semana, trafico actual, temperatura y velocidad de viento.
- Publicacion de entidades TrafficEnvironmentImpactForecast en Orion-LD.
- Visualizacion de prediccion y banda de confianza en ChartJS.

Valor para usuarios:
- Gestor municipal: capacidad de anticipacion operativa.
- Investigador: evaluacion cuantitativa de capacidad predictiva.

### F4. Motor explicativo LLM local (Ollama + Mistral)
Descripcion:
- Inferencia local sin API key externa.
- Contexto de entrada: metricas actuales, historico 6h y prediccion ML.
- Generacion de informe explicativo en espanol en menos de 3 segundos.
- Soporte a alertas push simuladas cuando NO2 supera 40 ug/m3.

Valor para usuarios:
- Gestor municipal: explicaciones accionables para justificar medidas.
- Ciudadania: narrativa comprensible del estado ambiental.

### F5. Visor 3D inmersivo de la ciudad (ThreeJS)
Descripcion:
- Modelo del centro de A Coruna con edificios extruidos desde OpenStreetMap.
- Nube volumetrica de contaminacion animada segun AQI.
- Modo time-lapse de las ultimas 24 horas en 30 segundos.
- Cambio entre vista ciudadana y vista tecnica con valores numericos.

Valor para usuarios:
- Gestor municipal e investigador: analisis espacial avanzado.
- Ciudadania: comprension intuitiva de la evolucion ambiental.

### F6. Sistema de alertas de zonas criticas
Descripcion:
- Generacion de alertas cuando se detectan umbrales criticos (por ejemplo NO2 > 40 ug/m3) o persistencia de impacto ambiental.
- Alertas orientadas a operacion municipal y comunicacion ciudadana.
- Priorizacion por severidad, zona y horizonte temporal.

Valor para usuarios:
- Gestor municipal: respuesta temprana.
- Ciudadania: prevencion y adaptacion de actividad diaria.

### F7. Interfaz responsiva ciudadana
Descripcion:
- Diseno mobile-first con indice ambiental simplificado tipo semaforo.
- Recomendaciones diarias contextualizadas por zona.
- Integracion con GreenRoute mediante accion "Cual es mi ruta mas sana hoy?".

Valor para usuarios:
- Ciudadania: acceso rapido y comprensible desde movil.
- Gestor municipal: mayor alcance de comunicacion publica.

## 4. Requisitos no funcionales

### 4.1 Interoperabilidad y modelo semantico
- Todas las entidades deben usar NGSI-LD (no NGSIv2).
- Uso de Smart Data Models definidos para:
  TrafficFlowObserved, ItemFlowObserved, TrafficEnvironmentImpact, TrafficEnvironmentImpactForecast, AirQualityObserved, NoiseLevelObserved, Device y DeviceModel.
- Relaciones NGSI-LD obligatorias:
  - TrafficEnvironmentImpact -> refersTo -> TrafficFlowObserved
  - TrafficEnvironmentImpactForecast -> basedOn -> TrafficEnvironmentImpact
  - AirQualityObserved -> measuredBy -> Device
  - NoiseLevelObserved -> measuredBy -> Device
  - Device -> hasModel -> DeviceModel

### 4.2 Plataforma y despliegue
- Contenerizacion con Docker y Docker Compose.
- Broker de contexto Orion-LD como nucleo de datos operacionales.
- Historizacion con QuantumLeap + CrateDB.
- Backend de negocio en Python FastAPI.

### 4.3 Visualizacion y experiencia
- Mapa con Leaflet + OSM + Leaflet.heat.
- Graficas de correlacion y prediccion con ChartJS.
- Analisis historico en Grafana embebido.
- Interfaz responsive para escritorio y movil.

### 4.4 Rendimiento
- Actualizacion de mapa y panel operativo cada 30 segundos.
- Generacion de explicacion LLM local < 3 segundos.
- Disponibilidad de dashboard y consultas operativas en tiempo real durante horas punta.

### 4.5 Calidad y mantenibilidad
- Trazabilidad entre PRD, architecture y data model.
- Datos de prueba realistas para A Coruna en todos los modulos.
- Configuracion por variables de entorno para despliegue reproducible.

## 5. Historias de usuario detalladas

### HU-01 (Gestor municipal) - Deteccion de zona critica
Como gestor municipal
Quiero identificar en el mapa las zonas con impacto ambiental persistente
Para activar medidas de mitigacion antes de que se agrave el episodio.

Detalles:
- Visualiza capa de impacto ambiental y persistencia > 2h.
- Filtra por contaminante y franja horaria.
- Consulta tendencia de la ultima hora en la misma pantalla.

### HU-02 (Gestor municipal) - Simulacion de ZBE
Como gestor municipal
Quiero simular la activacion de una ZBE en una zona y franja horaria
Para estimar reduccion esperada de NO2 y seleccionar la mejor estrategia.

Detalles:
- Consume prediccion TrafficEnvironmentImpactForecast.
- Compara escenario base vs escenario con restriccion.
- Registra historial de decisiones y eficacia.

### HU-03 (Ciudadania) - Consulta ambiental rapida
Como ciudadano
Quiero abrir la app en movil y ver un indice semaforo de mi barrio
Para saber rapidamente si es recomendable caminar o ir en bici.

Detalles:
- Vista simplificada con recomendacion diaria.
- Interpretacion inmediata sin conocimientos tecnicos.
- Enlace directo a ruta saludable.

### HU-04 (Ciudadania) - Ruta saludable
Como ciudadano
Quiero obtener una ruta que minimice exposicion a contaminacion y ruido
Para reducir el impacto en mi salud durante el desplazamiento.

Detalles:
- Compara ruta saludable con ruta mas corta.
- Muestra diferencia de tiempo y ganancia de salud.
- Usa datos en tiempo real de aire, ruido y trafico.

### HU-05 (Investigador) - Correlacion historica
Como investigador
Quiero analizar la relacion temporal entre trafico y contaminacion
Para validar hipotesis sobre eventos urbanos y dispersores atmosfericos.

Detalles:
- Consulta series historicas en Grafana/CrateDB.
- Exporta periodos comparables por zona.
- Cruza con eventos detectados (atasco, obra, evento masivo).

### HU-06 (Investigador) - Evaluacion de prediccion
Como investigador
Quiero comparar prediccion 6/12/24h frente a observacion real
Para medir rendimiento y ajustar el modelo.

Detalles:
- Observa banda de confianza en dashboard.
- Analiza errores por zona y franja horaria.
- Traza relacion con condiciones meteorologicas disponibles.

### HU-07 (Gestor municipal) - Explicacion automatica
Como gestor municipal
Quiero recibir una explicacion textual en espanol de un pico de contaminacion
Para comunicar de forma clara la causa probable y la evolucion esperada.

Detalles:
- Incluye contexto de metricas actuales, historico y forecast.
- Entrega respuesta en menos de 3 segundos.
- Permite activar alerta operativa cuando se supera umbral.

## 6. Criterios de aceptacion por funcionalidad

### Criterios F1 - Mapa de calor
- CA-F1-01: El mapa se centra en A Coruna (43.3713, -8.4194) al iniciar.
- CA-F1-02: Existen capas conmutables para AQI, ruido y trafico.
- CA-F1-03: El heatmap se actualiza automaticamente cada 30 segundos.
- CA-F1-04: Cada sensor muestra popup con metricas actuales y tendencia ultima hora.
- CA-F1-05: La codificacion de color sigue escala AQI europeo.

### Criterios F2 - Dashboard correlacion
- CA-F2-01: Se visualiza grafica de ejes duales (veh/h vs NO2/PM2.5).
- CA-F2-02: Se detectan eventos de atasco, obra y evento masivo por umbral.
- CA-F2-03: Grafana embebido consulta historicos sobre CrateDB.
- CA-F2-04: El usuario puede filtrar por zona y franja horaria.

### Criterios F3 - Prediccion ML
- CA-F3-01: El sistema genera prediccion para horizontes 6h, 12h y 24h.
- CA-F3-02: La prediccion usa Random Forest y LSTM con features definidas en contexto.
- CA-F3-03: Se publica entidad TrafficEnvironmentImpactForecast en Orion-LD.
- CA-F3-04: El dashboard muestra prediccion y banda de confianza.

### Criterios F4 - Motor LLM local
- CA-F4-01: El motor se ejecuta en local con Ollama + Mistral sin API key externa.
- CA-F4-02: El contexto de explicacion combina estado actual, historico 6h y forecast.
- CA-F4-03: El informe se genera en espanol y en menos de 3 segundos.
- CA-F4-04: Se emite alerta push simulada cuando NO2 supera 40 ug/m3.

### Criterios F5 - Visor 3D
- CA-F5-01: El visor representa el centro urbano de A Coruna con geometria OSM extruida.
- CA-F5-02: Se muestra nube volumetrica animada de contaminacion.
- CA-F5-03: Existe modo time-lapse de 24h en 30 segundos.
- CA-F5-04: Se permite alternar vista ciudadana y vista tecnica.

### Criterios F6 - Alertas de zonas criticas
- CA-F6-01: Se detectan condiciones de umbral y persistencia de impacto por zona.
- CA-F6-02: Las alertas incluyen severidad, zona y recomendacion operativa.
- CA-F6-03: Se registra historico de alertas para evaluacion posterior.

### Criterios F7 - Interfaz responsiva ciudadana
- CA-F7-01: La interfaz mobile-first muestra indice semaforo por barrio.
- CA-F7-02: Se muestran recomendaciones diarias legibles para usuario no tecnico.
- CA-F7-03: Incluye accion directa a GreenRoute para ruta saludable.
- CA-F7-04: Mantiene consistencia visual y funcional en escritorio y movil.

## 7. Trazabilidad funcional

- GreenRoute: F7 + HU-04 + entradas de F1/F2.
- UrbanPulse (nucleo): F1, F2, F3, F4.
- EcoZones: F6 + soporte de F3 y analitica F2.

## 8. Criterios de exito del producto

- Cobertura completa de entidades NGSI-LD requeridas y sus relaciones.
- Capacidad de monitorizacion en tiempo real de las seis zonas de sensores definidas.
- Generacion de predicciones 6/12/24h y explicaciones accionables para decision municipal.
- Experiencia ciudadana mobile-first util para ruta y exposicion diaria.

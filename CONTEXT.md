---BEGIN CONTEXT---
UrbanPulse Coruña — Contexto del proyecto
Visión general
UrbanPulse Coruña es una plataforma FIWARE NGSI-LD de
monitorización ambiental urbana que correlaciona en tiempo real
la contaminación atmosférica, el ruido urbano y los flujos de
tráfico de A Coruña. Actúa como gemelo digital ambiental de la
ciudad: ingiere datos de sensores IoT, los almacena en Orion-LD,
genera predicciones mediante modelos ML y produce explicaciones
automáticas en español usando un LLM local (Ollama + Mistral).
El proyecto fusiona tres conceptos originales en una sola
plataforma:
Las tres ideas fusionadas
1. GreenRoute — Navegador de rutas saludables
Calcula la ruta peatonal o ciclista que minimiza la exposición
del ciudadano a contaminación y ruido, no el tiempo de
desplazamiento. Genera un índice de salubridad por tramo de
calle combinando AirQualityObserved + NoiseLevelObserved +
TrafficFlowObserved en tiempo real.
Factor diferencial: ninguna app de navegación optimiza
salud ciudadana; todas optimizan tiempo o distancia.
2. UrbanPulse — Dashboard de bienestar urbano (núcleo)
Correlaciona eventos de tráfico (atascos, obras, eventos
masivos detectados via ItemFlowObserved) con picos de
contaminación. El módulo LLM local genera explicaciones
contextuales en español del tipo:
"El pico de NO₂ en la Ronda de Outeiro (89 µg/m³ a las
18:32h) está causado por la confluencia del tráfico de
salida y viento SW. Se prevé reducción del 34% a las 20h."
Factor diferencial: LLM local como módulo explicativo
actionable — novedad técnica alta, muy valorada en la práctica.
3. EcoZones — Zonas de bajas emisiones dinámicas
Simula un sistema municipal que activa y desactiva zonas de
bajas emisiones (ZBE) automáticamente según los valores de
TrafficEnvironmentImpact en tiempo real. Panel de control para
gestores municipales con propuesta de restricciones.
Factor diferencial: alineado con políticas reales vigentes
(Madrid Central, Barcelona Superilles, ZBE europeas 2025).
La visualización 3D con ThreeJS maximiza la nota en el criterio
de visualizaciones.
Funcionalidades principales
F1 · Mapa de calor ambiental en tiempo real
Leaflet + OSM centrado en A Coruña (43.3713, -8.4194)
Capas toggleables: calidad del aire (AQI), ruido (dB),
intensidad de tráfico (veh/h)
Heatmap dinámico con Leaflet.heat, actualización cada 30s
Marcadores de sensores clicables con popup de métricas
actuales y tendencia última hora
Código de colores según índice AQI europeo (verde/amarillo/
naranja/rojo/violeta)
F2 · Dashboard de correlación tráfico-contaminación
ChartJS con ejes duales: tráfico (veh/h) vs NO₂/PM2.5 (µg/m³)
por hora del día
Detección automática de eventos: atasco (tráfico > umbral),
obra (tráfico anómalo + bajo ruido nocturno), evento masivo
(ItemFlowObserved > umbral)
Grafana embebido para análisis histórico profundo con
datasource CrateDB
F3 · Predicción ML 6/12/24h
Modelo Random Forest (scikit-learn) + LSTM (TensorFlow)
entrenado con 30 días de datos históricos simulados
Features: hora del día, día de semana, tráfico actual,
temperatura, velocidad del viento
Genera entidades TrafficEnvironmentImpactForecast en Orion-LD
Visualización de predicción + banda de confianza en ChartJS
F4 · Motor explicativo LLM local
Ollama ejecutando Mistral-7B o LLaMA-3 en local (sin API key)
Contexto: métricas actuales de los sensores + histórico 6h +
predicción ML
Genera informe en español en < 3 segundos
Alertas push simuladas (email/WhatsApp) cuando NO₂ > 40µg/m³
F5 · Visor 3D inmersivo (ThreeJS)
Centro de A Coruña modelado con edificios extruidos desde
datos OpenStreetMap
Nube volumétrica de contaminación animada y coloreada según
nivel AQI real
Modo time-lapse: evolución de la contaminación en las últimas
24h en 30 segundos
Toggle entre vista ciudadana y vista técnica (valores numéricos)
F6 · Interfaz responsiva ciudadana
Vista mobile-first con índice ambiental del barrio
simplificado (semáforo)
Recomendaciones diarias: "Hoy el aire en el Paseo Marítimo
es excelente. Buen día para ir en bici al trabajo."
Integración con GreenRoute: botón "¿Cuál es mi ruta más
sana hoy?"
F7 · Panel EcoZones (gestión municipal)
Mapa de zonas con impacto ambiental persistente
(TrafficEnvironmentImpact > umbral durante > 2h)
Propuesta automática de activación de ZBE con simulación
de impacto esperado
Histórico de activaciones y métricas de eficacia
Smart Data Models usados (NGSI-LD)
Todos los modelos deben usar NGSI-LD, nunca NGSIv2.
Las entidades deben estar relacionadas entre sí mediante
atributos Relationship.
Entidad	Dominio	Rol
TrafficFlowObserved	Transportation	Flujo vehículos por tramo
ItemFlowObserved	Transportation	Flujo peatones/bicicletas
TrafficEnvironmentImpact	Environment	Impacto contaminación por zona
TrafficEnvironmentImpactForecast	Environment	Predicción ML 6/12/24h
AirQualityObserved	Environment	NO₂, PM2.5, O₃, CO
NoiseLevelObserved	Environment	Contaminación acústica dB(A)
Device	Device	Sensor IoT físico/virtual
DeviceModel	Device	Modelo/tipo de sensor
Relaciones clave:
TrafficEnvironmentImpact → refersTo → TrafficFlowObserved
TrafficEnvironmentImpactForecast → basedOn → TrafficEnvironmentImpact
AirQualityObserved → measuredBy → Device
NoiseLevelObserved → measuredBy → Device
Device → hasModel → DeviceModel
Stack tecnológico completo
Capa	Tecnología	Versión recomendada
Context Broker	Orion-LD	1.5+
IoT Agent	IoT Agent JSON	latest
Históricos	QuantumLeap + CrateDB	latest
Dashboards	Grafana	10+
Backend	Python FastAPI	3.11+
ML	scikit-learn + TensorFlow	latest
LLM local	Ollama + Mistral-7B	latest
Mapa	Leaflet + OSM + Leaflet.heat	1.9+
Gráficos	ChartJS	4+
3D	ThreeJS	r128+
Datos	Pandas + GeoPandas	latest
Contenedores	Docker + Docker Compose	24+
Ubicaciones reales de sensores en A Coruña
ID	Nombre	Lat	Lon	Tipo zona
sensor-001	Avda. de Finisterre	43.3713	-8.4194	Alto tráfico
sensor-002	Ronda de Outeiro	43.3687	-8.4071	Ronda periurbana
sensor-003	Cuatro Caminos	43.3698	-8.4089	Nodo transporte
sensor-004	Paseo Marítimo	43.3714	-8.3967	Costa, baja contaminación
sensor-005	Torre Hércules	43.3858	-8.4066	Referencia histórica
sensor-006	Monte San Pedro	43.3782	-8.4397	Zona verde periférica
Criterios de valoración y cómo los maximizamos
Criterio	Estrategia
Originalidad	Fusión única GreenRoute + UrbanPulse + EcoZones. LLM local explicativo, índice de salubridad por ruta.
Variedad entidades	8 modelos NGSI-LD con Relationship entre todos ellos. Cross-sector: Device + Environment + Transportation.
Visualizaciones	4 tecnologías distintas: Leaflet heatmap, ChartJS dual-axis, ThreeJS 3D volumétrico, Grafana histórico.
Tecnologías	FastAPI + ML (RF+LSTM) + LLM local + IoT Agent MQTT + QuantumLeap + Docker + GeoPandas.

Funcionalidades adicionales
Índice de Presión Urbana (IPU)
Score compuesto por zona calculado en tiempo real:
IPU = w1·(tráfico_normalizado)
+ w2·(flujo_peatonal_normalizado)
+ w3·(NO₂_normalizado)
+ w4·(ruido_normalizado)
Entidades involucradas:
TrafficFlowObserved → componente vehicular
ItemFlowObserved → componente peatonal/ciclista
AirQualityObserved → componente atmosférico
NoiseLevelObserved → componente acústico
TrafficEnvironmentImpact → resultado del IPU por zona
El IPU alimenta directamente EcoZones para decidir
activación de ZBE y GreenRoute para ponderar rutas.
Funcionalidad adicional: Simulador de escenarios ZBE
Usando TrafficEnvironmentImpactForecast, el panel EcoZones
permite simular: "Si activamos ZBE en zona X mañana 8-10h,
el NO₂ previsto baja de 89 µg/m³ a 52 µg/m³ (-42%)".
Visualizado en ThreeJS como comparativa before/after.
Modelo transversal: WeatherObserved
Añadir WeatherObserved (temperatura, velocidad/dirección
del viento, humedad) como feature del modelo ML y como
contexto para el LLM explicativo. El viento en A Coruña
es el principal factor de dispersión de contaminantes.
Features ML adicionales: wind_speed, wind_direction,
temperature, humidity.
GreenRoute — algoritmo concreto
Cargar grafo de calles de A Coruña con osmnx
Para cada arista del grafo, calcular índice de
salubridad = f(AirQuality, Noise, Traffic) del
sensor más cercano (interpolación IDW)
Shortest path con networkx usando peso =
1/índice_salubridad (minimizar exposición)
Comparar ruta saludable vs ruta más corta:
mostrar diferencia en tiempo (+X min) y ganancia
en salud (-Y% exposición NO₂)
 

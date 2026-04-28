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

## 9. Estado de implementacion - Issue #1

### 9.1 Objetivo de la entrega
Implementar la infraestructura FIWARE NGSI-LD base para habilitar ingesta, gestion de contexto, historizacion y visualizacion inicial.

### 9.2 Entregables tecnicos
- Stack base en `docker-compose.yml` con Orion-LD, IoT Agent JSON, QuantumLeap, CrateDB y Grafana.
- Configuracion centralizada en `.env` para puertos, versiones y credenciales.
- Script operativo `services/healthcheck.sh` para validar disponibilidad de servicios.
- Provision de suscripcion Orion-LD -> QuantumLeap para todas las entidades del modelo.

### 9.3 Criterios de aceptacion de infraestructura
- El despliegue con `docker compose --env-file .env up -d` finaliza sin errores.
- `services/healthcheck.sh` devuelve codigo de salida 0 con todos los servicios en estado OK.
- Existe al menos una suscripcion activa en Orion-LD que notifica a `http://quantumleap:8668/v2/notify`.
- La suscripcion incluye todos los tipos de entidad definidos en `docs/data_model.md`.

## 10. Estado de implementacion - Issue #3: Backend FastAPI con ML y LLM

### 10.1 Objetivo de la entrega
Implementar el backend FastAPI como capa de orquestacion que exponga API REST para el frontend, integre contexto NGSI-LD de Orion-LD, consulte historicos de QuantumLeap/CrateDB, genere predicciones ML y produzca explicaciones automaticas en español con Ollama local.

### 10.2 Entregables tecnicos
- **backend/main.py**: FastAPI con 6 endpoints REST, middleware CORS, orquestacion de clientes.
- **backend/orion_client.py**: cliente NGSI-LD para consultas de estado actual a Orion-LD.
- **backend/quantumleap_client.py**: cliente CrateDB para series historicas.
- **backend/ml_model/train.py**: pipeline de entrenamiento RandomForest con 13 features y 3 targets.
- **backend/ml_model/predict.py**: generacion de entidades TrafficEnvironmentImpactForecast NGSI-LD.
- **backend/llm/explainer.py**: llamada a Ollama Mistral local con fallback heurístico.
- **backend/config.py**: configuracion de settings por variables de entorno.
- **backend/common.py**: utilidades NGSI-LD, helpers de feature engineering y constantes.
- **backend/requirements.txt**: dependencias (fastapi, uvicorn, requests, scikit-learn, numpy).

### 10.3 Endpoints Implementados
- GET /api/sensors — lista de sensores con estado actual (traffic, air quality, noise, impact)
- GET /api/sensors/{id}/history — series historicas por sensor (filtrable por horas)
- GET /api/impact — impacto ambiental observado por zona
- GET /api/forecast — predicciones 6/12/24h con confianza
- GET /api/alerts — alertas activas (NO2 > 40, impact > 70, noise > 65)
- POST /api/explain — explicacion en español con contexto actual + historico + forecast

### 10.4 Criterios de aceptacion de backend
- El backend arranca sin errores con `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`.
- GET /api/sensors devuelve 200 con lista de 6 sensores y sus metricas actuales.
- GET /api/sensors/{id}/history devuelve 200 con serie temporal por sensor.
- GET /api/forecast devuelve 200 con predicciones para horizontes 6, 12, 24h.
- POST /api/explain devuelve 200 con explicacion en español < 3 segundos.
- Headers CORS permiten acceso desde origen frontend (* o configurado).
- El modelo ML se entrena automaticamente si no existe artefacto o se fuerza entrenamiento.
- Ollama fallback devuelve explicacion heurística cuando LLM no disponible.

### 10.5 Arquitectura Interna
- OrionClient y QuantumLeapClient encapsulan acceso a datos con manejo de timeouts.
- MLModel (RandomForest) predice NO2, PM2.5, impactScore usando 13 features.
- OllamaExplainer construye prompt con contexto actual + historico 6h + forecast y llama Mistral.
- Todos los clientes son inicializados al startup de FastAPI y reutilizados en rutas.
- Las rutas actuan como orquestadores de logica, no contienen SQL o NGSI-LD directo.

## 11. Estado de implementacion - Issue #4: Frontend Web Responsivo con Leaflet, ChartJS y ThreeJS

### 11.1 Objetivo de la entrega
Implementar frontend web responsivo mobile-first que ofrezca visualización integrada de monitoreo ambiental urbano con mapa interactivo (Leaflet + heatmap dual mode), gráficos de correlación trafico-contaminación (ChartJS con ejes duales y bandas de confianza), visor 3D inmersivo (ThreeJS con edificios extruidos y nube volumétrica de contaminación), y panel LLM para explicaciones automáticas en español.

### 11.2 Entregables técnicos
- **frontend/index.html**: Single-page template responsivo con layout 3 columnas (sidebar | map | metrics), tema oscuro profesional.
- **frontend/package.json**: Dependencias (Leaflet, ChartJS, ThreeJS, Socket.io).
- **frontend/css/theme.css**: Paleta oscura profesional (#0a0e27, #12152b, acentos #00d4ff), variables CSS, componentes reutilizables.
- **frontend/css/layout.css**: Grid layout responsive con breakpoints (320px/480px/768px/1024px/1440px).
- **frontend/js/main.js**: Punto de entrada de la aplicación, inicialización de módulos, manejo de eventos.
- **frontend/js/api.js**: Wrapper HTTP con caché (TTL configurable) para todos los endpoints backend.
- **frontend/js/websocket.js**: Cliente Socket.io con reconexión automática, fallback a simulación de datos.
- **frontend/js/map.js**: Leaflet map centrado en A Coruña, marcadores dinámicos, heatmap dual mode (real-time/histórico 24h).
- **frontend/js/sidebar.js**: Lista de sensores, controles de capas (toggle heatmap, toggle marcadores, radio modo), alertas, interacciones.
- **frontend/js/charts.js**: ChartJS con 3 gráficos: dual-axis (tráfico vs NO₂), evolución 24h, radar chart índices ambientales.
- **frontend/js/viewer3d.js**: ThreeJS escena con edificios procedurales, nube volumétrica de contaminación animada, time-lapse 24h.
- **frontend/js/llm-panel.js**: Panel integrado en sidebar para explicaciones LLM con caché, POST /api/explain, fallback heurístico.

### 11.3 Características Implementadas

#### 11.3.1 Layout Responsivo Mobile-First
- **3 columnas adaptive**: Sidebar (sensores/controles) | Mapa central | Panel métricas (charts/3D)
- **Breakpoints**: Mobile < 768px (stack vertical, sidebar colapsable), Tablet 768-1024px (2-col), Desktop > 1024px (3-col)
- **Componentes responsive**: Botones 44px min tap target, fuentes escaladas (14px mobile, 16px desktop)
- **No horizontal scroll** en ningún breakpoint, viewport meta tag configurado

#### 11.3.2 Tema Oscuro Profesional
- **Paleta**: Fondo #0a0e27, secundario #12152b, terciario #1a1f3a
- **Acentos**: Azul ciano #00d4ff (primario), naranja #ff6b6b (alertas), verde #4ade80 (ok)
- **Tipografía**: System fonts (Segoe UI, Roboto, Oxygen), line-height 1.5, responsive font-sizing
- **Transiciones smooth**: 150-500ms ease-in-out, animaciones (fadeIn, slideInUp, pulse)
- **Componentes**: Botones hover/active, cards con sombra, inputs focus personalizado, scrollbar oscuro

#### 11.3.3 Mapa Leaflet + Heatmap Dual Mode
- **Mapa base**: Leaflet + OpenStreetMap, centrado en 43.3713, -8.4194, zoom 13
- **Marcadores de sensores**: 6 marcadores dinámicos con iconos color según severidad NO₂ (verde/naranja/rojo)
- **Popup interactivo**: Muestra NO₂, PM2.5, tráfico, ruido, impacto + botón "Ver detalles"
- **Dual heatmap modes**:
  - `real-time`: Actualiza cada 5-10s con valores actuales de sensores
  - `historical`: Agrega datos 24h por sensor, interpola mapa de calor suave
  - Toggle radio button para cambiar modo
- **Control de capas**: Checkbox toggle heatmap visibility, checkbox toggle marcadores
- **Actualización en tiempo real** vía WebSocket events (sensor_update)

#### 11.3.4 Gráficos ChartJS con Correlación y Predicción
- **Chart 1: Tráfico vs NO₂ (Dual-axis)**:
  - Eje Y izquierdo: NO₂ línea roja + banda confianza (relleno transparente, borde punteado)
  - Eje Y derecho: Tráfico barras azul ciano
  - Datos: 24h histórico + predicción 6/12/24h (líneas punteadas)
  - Tooltips personalizados oscuros, leyenda interactiva
- **Chart 2: Evolución 24h**:
  - Línea NO₂ histórico vs 3 predicciones con colores distintos
  - Eje X horas 0-24, eje Y NO₂ 0-150 µg/m³
- **Chart 3: Radar chart índices ambientales**:
  - 5 ejes: NO₂, PM2.5, Ruido, Tráfico, Impacto
  - Valores normalizados 0-100
  - Actualiza en tiempo real en dataset

#### 11.3.5 Visor 3D Inmersivo con ThreeJS
- **Geometría urbana**:
  - Grid 10x10 de edificios procedurales (altura 20-200m)
  - Colores variables por land-use, materiales con metalness/roughness
  - Plano de terreno con textura oscura
- **Iluminación**: Ambient light, directional sun light (sombras), hemisphere light
- **Nube volumétrica de contaminación**:
  - 2000 partículas con colores verde→amarillo→rojo por intensidad NO₂
  - Opacidad interpolada según valores actuales de sensores
  - Rotación animada
- **Marcadores de sensores**:
  - Esferas azul ciano en ubicaciones lat/lon (proyección Web Mercator)
  - Animaciones TWEEN.js (bounce suave)
- **Time-lapse mode**:
  - Slider timeline 0-24h
  - Play button anima automáticamente 24h en 30s
  - Nube volumétrica cambia color con la hora histórica
  - Cargas datos históricos de 3 primeros sensores
- **Controles cámara**: Orbit (mouse drag/touch swipe), zoom (scroll/pinch), reset a home view
- **Responsive**: Canvas llena espacio disponible, resize automático

#### 11.3.6 Panel LLM Explainer
- **Integrado en sidebar**: Sección desplegable con explicación IA
- **Trigger**: Click automático o botón "Explicación IA" en selección sensor
- **Petición**: POST /api/explain con {sensor_id, include_history_hours: 6}
- **Renderizado**: Texto español con fuente, timestamp, botón refrescar
- **Caché**: 2 minutos por sensor (no re-query frecuente)
- **Fallback**: Explanation heurística si Ollama no disponible
- **Indicador fuente**: "🤖 Ollama" o "⚙️ Heurístico"

#### 11.3.7 Integración Tiempo Real
- **WebSocket Socket.io**: Conexión a `http://localhost:5173` para eventos en vivo
- **Eventos escuchados**: `sensor_update`, `forecast_update`, `alert_new`, `alert_resolved`, `llm_response`
- **Fallback simulación**: Si WebSocket no disponible, simula datos cada 5 segundos
- **Indicador estado**: LED online/offline en header

#### 11.3.8 Interfaz Sidebar
- **Lista de sensores**: 6 elementos con nombre, NO₂ actual, score impacto
- **Estados activo**: Highlighting sensor seleccionado, centra mapa
- **Sección alertas**: Lista scrollable de alertas activas con severidad (color)
- **Mobile**: Sidebar colapsable hamburger button, cierra al seleccionar sensor

### 11.4 Criterios de Aceptación Frontend
- **CA-FE-01**: Layout responsive valida en 320px, 480px, 768px, 1024px, 1440px sin scroll horizontal
- **CA-FE-02**: Mapa Leaflet centra en A Coruña, muestra 6 marcadores, heatmap renderiza con color gradient
- **CA-FE-03**: Heatmap dual mode: toggle real-time/histórico cambia datos y visualización
- **CA-FE-04**: Gráfico dual-axis muestra tráfico + NO₂ + banda confianza, tooltips funcionan
- **CA-FE-05**: Gráfico radar actualiza en tiempo real con datos sensor seleccionado
- **CA-FE-06**: Visor 3D carga: edificios procedurales visibles, nube volumétrica coloreada por NO₂, time-lapse reproduce 24h
- **CA-FE-07**: Panel LLM click sensor → POST /api/explain → renderiza texto español < 3s
- **CA-FE-08**: WebSocket conecta y actualiza heatmap en tiempo real, o fallback a simulación
- **CA-FE-09**: Tema oscuro consistente, botones 44px mín, accesibilidad WCAG A nivel base
- **CA-FE-10**: Controles cámara 3D funcionan (orbit mouse, zoom scroll, pinch móvil)

### 11.5 Stack Técnico Frontend
- **Plantilla**: HTML5 semántico, meta viewport responsivo
- **Estilos**: CSS3 con Grid/Flexbox, variables CSS, media queries breakpoints, SCSS-ready
- **Mapeo**: Leaflet 1.9.x + OpenStreetMap + Leaflet.heat 0.2.x
- **Gráficos**: ChartJS 4.x con múltiples types (bar, line, radar)
- **3D**: ThreeJS r164 con geometrías estándar, iluminación, TWEEN.js animaciones
- **Comunicación**: Socket.io 4.x + HTTP fetch con caché local
- **Build**: Vite 5.x (dev server, producción build)

### 11.6 Arquitectura Interna
- **main.js**: Inicializa secuencialmente map → sidebar → charts → 3D viewer → LLM panel
- **api.js**: Capa abstracta HTTP con caché TTL y error handling
- **websocket.js**: Maneja conexión Socket.io y emite eventos internos
- **map.js**: Instancia Leaflet, gestiona marcadores y heatmap, reacciona a eventos WebSocket
- **charts.js**: Crea 3 instancias ChartJS, vinculadas a eventos sensor-selected y WebSocket
- **viewer3d.js**: Escena ThreeJS inicializada, carga datos histórico para time-lapse, renderiza en animation loop
- **sidebar.js**: Observa DOM, vinculado a map.selectSensor, carga alertas, actualiza lista en tiempo real
- **llm-panel.js**: Observa sensor-selected event, cachea respuestas, renderiza explicación

### 11.7 Dependencias Externas Asumidas
- Backend corriendo en `http://localhost:8000` con endpoints /api/sensors, /api/forecast, /api/explain, etc.
- Socket.io servidor opcional en `http://localhost:5173` (fallback simulación si no disponible)
- Ollama disponible en `http://localhost:11434` para LLM (fallback heurístico si no disponible)

### 11.8 Siguientes Pasos
- Instalar dependencias: `npm install` en carpeta frontend/
- Desarrollar con `npm run dev` (Vite dev server)
- Build producción: `npm run build`
- Servir static build con web server (nginx, Apache, etc.)

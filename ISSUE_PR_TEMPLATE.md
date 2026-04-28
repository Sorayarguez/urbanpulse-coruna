# Issue #4: Frontend Web Responsivo con Leaflet, ChartJS y ThreeJS

## Descripción

Implementación completa del frontend responsivo para UrbanPulse Coruña con:
- Mapa interactivo Leaflet + OpenStreetMap con capas de calor (heatmap) dual mode (real-time/histórico)
- Mapa de calor dinámico para NO₂, tráfico y ruido con Leaflet.heat
- Marcadores clicables de sensores con popup de datos actuales
- Gráficos ChartJS con ejes duales (tráfico vs NO₂), evolución 24h, predicción ML con banda de confianza
- Radar chart para índices ambientales por zona
- Visor 3D inmersivo con ThreeJS (edificios extruidos, nube volumétrica de contaminación, modo time-lapse)
- Panel LLM con llamadas a POST `/api/explain`
- Layout responsivo mobile-first (3 columnas: sidebar, mapa, métricas)
- Tema oscuro profesional

## Detalles técnicos

### Estructura de archivos
```
frontend/
├── index.html                 # Single-page HTML template, responsive layout
├── package.json              # Frontend dependencies
├── css/
│   ├── theme.css            # Dark professional theme with CSS variables
│   └── layout.css           # Responsive 3-column layout, breakpoints
└── js/
    ├── main.js              # App initialization and event handling
    ├── api.js               # HTTP API wrapper with caching
    ├── websocket.js         # Real-time WebSocket connection & simulation
    ├── map.js               # Leaflet map initialization, heatmap (dual mode)
    ├── sidebar.js           # Sensor list, layer controls, alerts
    ├── charts.js            # ChartJS: dual-axis, evolution, radar charts
    ├── viewer3d.js          # ThreeJS: buildings, volumetric cloud, time-lapse
    └── llm-panel.js         # LLM explainer with caching
```

### Características implementadas

#### 1. **Frontend/index.html - Layout Responsivo**
- Single-page app con estructura semántica
- 3 columnas adaptive: sidebar (sensors/controls) | map (central) | metrics (charts/3D)
- Mobile-first design: stack vertical < 768px, 2-col 768-1024px, 3-col > 1024px
- Meta tags viewport para responsividad
- CDN links: Leaflet, ChartJS, ThreeJS, Socket.io
- Tabs para cambiar entre vistas (mapa, gráficos, visor 3D)

#### 2. **CSS - Tema oscuro profesional**
- `css/theme.css`: Paleta oscura (#0a0e27, #12152b, #1a1f3a), acentos azules (#00d4ff) y naranjas
- Variables CSS para colores, spacing, transiciones, bordes
- Componentes reutilizables: botones, badges, cards, inputs
- Animaciones smooth (fadeIn, slideInUp, pulse)
- Scrollbar personalizado, hover effects, estados focus
- `css/layout.css`: Grid layout responsive, breakpoints 320px/480px/768px/1024px/1440px
- Sobrescritura Leaflet para tema oscuro

#### 3. **js/api.js - API HTTP Wrapper**
- Funciones para todos los endpoints: `/api/sensors`, `/api/sensors/{id}/history`, `/api/impact`, `/api/forecast`, `/api/alerts`, `/api/explain`
- Sistema de caché con TTL configurable (5min sensores, 30min histórico, etc.)
- Error handling y retry logic
- POST `/api/explain` para obtener explicaciones LLM

#### 4. **js/websocket.js - Conexión en tiempo real**
- Socket.io client con reconexión automática (exponential backoff)
- Event listeners: `sensor_update`, `forecast_update`, `alert_new`, `alert_resolved`, `llm_response`
- Fallback mode: simulación de datos si WebSocket no está disponible
- Manejo de estado de conexión (online/offline)

#### 5. **js/map.js - Leaflet Map + Heatmap**
- Mapa centrado en A Coruña (43.3713, -8.4194), zoom 13
- **Dual heatmap modes**:
  - `realtime`: Usa valores actuales de sensores, actualiza cada 5-10s
  - `historical`: Agrega datos 24h históricos por sensor, interpola heatmap
  - Toggle radio button para cambiar modo
- **Marcadores dinámicos**: 6 sensores con colores por severidad (verde/naranja/rojo según NO₂)
- **Popup de sensor**: Muestra NO₂, PM2.5, tráfico, ruido, impacto + botón "Ver detalles"
- **Capas**: Toggle heatmap, toggle marcadores
- Actualización en tiempo real vía WebSocket

#### 6. **js/sidebar.js - Sensor List & Controls**
- **Sensor list**: 6 sensores, estado actual (NO₂, impacto)
- Selección de sensor → destaca en lista, centra mapa, carga gráficos
- **Capas toggle**: Checkbox heatmap, checkbox marcadores, radio modo heatmap
- **Alertas section**: Lista scrollable de alertas activas (color por severidad)
- **Mobile**: Sidebar colapsable (hamburger menu)
- Actualización en tiempo real de valores

#### 7. **js/charts.js - ChartJS Dashboards**
- **Chart 1: Traffic vs NO₂ (Dual-axis)**
  - Eje Y izquierdo: NO₂ línea + banda confianza (relleno + borde punteado)
  - Eje Y derecho: Tráfico barras
  - Datos: 24h histórico + predicción ML (6h, 12h, 24h) como líneas punteadas
- **Chart 2: Evolución 24h**
  - Línea NO₂ histórico vs predicciones de 3 horizontes
- **Chart 3: Radar chart índices ambientales**
  - 5 ejes: NO₂, PM2.5, ruido, tráfico, impacto
  - Valores normalizados 0-100
  - Actualiza en tiempo real
- Tooltips oscuros, leyendas personalizadas
- Resize automático en tab switch

#### 8. **js/viewer3d.js - ThreeJS 3D Immersive Viewer**
- **Escena 3D**: Fondo #0a0e27, iluminación (ambient + sun + hemisphere)
- **Edificios**: Grid 10x10 de edificios procedurales (altura 20-200m, colores variables)
- **Marcadores sensores**: Esferas azules en ubicaciones de sensores (lat/lon → proyección Web Mercator)
- **Nube volumétrica**: Sistema de partículas (2000 partículas, colores verde→rojo por intensidad)
  - Opacidad y color interpolados según NO₂ actual
- **Time-lapse mode**:
  - Slider timeline 0-24h
  - Play button anima a través de 24h en 30s
  - Nube volumétrica cambia color/intensidad con hora
  - Carga datos históricos 24h para 3 primeros sensores
- **Controles cámara**: Orbit (mouse drag/touch swipe), zoom (scroll/pinch)
- Animaciones TWEEN.js para movimiento suave
- Responsive canvas

#### 9. **js/llm-panel.js - LLM Explainer**
- Panel integrado en sidebar
- Click "Explicación IA" o auto-trigger en selección sensor
- POST `/api/explain` con `{sensor_id, include_history_hours: 6}`
- Renderiza texto español en panel con fuente, timestamp, botón refrescar
- Caché 2 minutos (no re-query mismo sensor frecuentemente)
- Fallback explanation si Ollama no disponible

#### 10. **js/main.js - App Entry Point**
- Inicialización secuencial de módulos
- Setup event handlers globales
- Conexión WebSocket (fallback a simulación si falla)
- Error handling y página de error
- Manejo menú mobile

### Responsive Design Breakpoints
- **Mobile** (< 768px): Stack vertical (sidebar → map → metrics), sidebar colapsable
- **Tablet** (768-1024px): 2-col (sidebar | map + charts apilados)
- **Desktop** (1024-1440px): 3-col clásico (sidebar | map | metrics)
- **Desktop Large** (> 1440px): 3-col con méttricas 4-col

### Integraciones
- **Backend API**: GET `/api/sensors`, GET `/api/sensors/{id}/history`, POST `/api/explain`, etc.
- **WebSocket**: Recibe `sensor_update`, `forecast_update`, `alert_new` en tiempo real
- **Caché**: Sistema interno con TTL configurable

### Tema Dark Professional
- Paleta: `#0a0e27` (bg), `#12152b` (secondary), `#00d4ff` (accent), `#ff6b6b` (alerts)
- Tipografía: Segoe UI, Roboto, Oxygen (system fonts)
- Sombras y bordes sutiles, transiciones smooth 150-500ms
- Botones con hover/active states

## Pruebas de validación

1. **Layout responsive**: Pruebar en breakpoints (320px, 480px, 768px, 1024px, 1440px)
2. **Mapa Leaflet**: Centrado en A Coruña, 6 marcadores visibles, heatmap renders
3. **Gráficos**: Dual-axis carga datos, banda confianza visible, radar actualiza
4. **3D viewer**: Buildings render, nube volumétrica visible, time-lapse juega
5. **WebSocket**: Datos real-time actualizan heatmap/charts, o fallback a simulación
6. **LLM panel**: Click sensor → POST /api/explain → texto español renderiza
7. **Mobile**: Sidebar colapsable, no horizontal scroll, botones 44px mín

## Conocimientos previos asumidos
- Backend corriendo en `http://localhost:8000` con endpoints API
- Socket.io servidor en `http://localhost:5173` (o fallback a simulación)
- Ollama disponible en `http://localhost:11434` para LLM (o fallback heurístico)

## Siguientes pasos
1. Instalar dependencias: `npm install` en carpeta `frontend/`
2. Deployar con Vite: `npm run dev` o `npm run build`
3. Abrir `index.html` en navegador (o servir con Vite dev server)
4. Backend WebSocket integration (optional, app funciona con simulación)

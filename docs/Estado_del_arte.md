# Estado del arte

UrbanPulse A Coruña se sitúa en la intersección de tres líneas que hoy convergen en las ciudades europeas: monitorización ambiental, gestión de tráfico y explotación interoperable de datos urbanos. La madurez del mercado ya no depende sólo de disponer de sensores o paneles, sino de integrar datos heterogéneos en tiempo real, correlacionarlos y convertirlos en decisiones útiles para administración y ciudadanía.

## 1. Marco europeo: FIWARE y Copernicus

FIWARE ha consolidado un enfoque de referencia para ciudades inteligentes basado en estándares abiertos, gestión de contexto y modelos de información comunes. Su propuesta Smart Cities destaca por romper silos verticales, permitir interoperabilidad entre sistemas y publicar datos en tiempo real a través de APIs estándar. El núcleo técnico sigue siendo Orion Context Broker, reforzado por una arquitectura que facilita ingestión IoT, tratamiento histórico, cuadros de mando y reutilización de datos entre dominios.

Copernicus aporta la otra mitad del panorama europeo: observación terrestre, servicios de atmósfera, clima, tierra, emergencias y mar. Para monitorización urbana, el valor está sobre todo en Copernicus Atmosphere Service, que ofrece productos y predicciones de calidad del aire, y en los hubs temáticos orientados a salud y transición energética. Es una capa excelente para contexto regional y forecast, pero no sustituye la granularidad urbana de los sensores locales ni la relación causal con el tráfico.

La conclusión práctica es clara: FIWARE resuelve la interoperabilidad operacional de la ciudad, mientras que Copernicus aporta el contexto geoambiental y la capacidad de previsión a escala regional o supramunicipal. UrbanPulse puede explotar ambas capas para cerrar el hueco entre observación local y contexto europeo.

Fuentes: [FIWARE Smart Cities](https://www.fiware.org/smart-cities/), [Copernicus Services](https://www.copernicus.eu/en/copernicus-services), [Copernicus home](https://www.copernicus.eu/en).

## 2. Ciudades comparables

### Madrid

Madrid dispone de una infraestructura madura de movilidad y calidad del aire. El portal [Aire de Madrid](https://airedemadrid.madrid.es/) publica datos medidos en estaciones de vigilancia, estimaciones por calle y previsiones de NO2, O3, PM10 y PM2.5. En paralelo, el portal municipal muestra incidencias de tráfico y afecciones a la movilidad, con páginas específicas para grandes obras, cortes y alteraciones del flujo urbano. El punto fuerte es la riqueza de datos y la actualización continua; la debilidad es que tráfico y contaminación siguen expuestos en canales diferenciados, con poca inferencia conjunta hacia el ciudadano.

### Barcelona

Barcelona ofrece un caso especialmente interesante por la convivencia de movilidad sostenible, zonas de bajas emisiones, red de vigilancia de calidad del aire y una capa pública de información urbana muy visible. El portal municipal integra movilidad, transporte y servicios urbanos, y la ciudad muestra de forma explícita el estado de la calidad del aire en estaciones como Eixample, Poblenou, Sants, Gràcia o Vall d’Hebron. Es un referente por su orientación a política pública, pero la correlación tráfico-contaminación no aparece como un servicio analítico nativo; se presenta sobre todo como contexto informativo y apoyo a la toma de decisiones.

### Santander Smart City

Santander es un referente histórico en sensorización urbana y experimentación IoT. Su ecosistema se asocia al proyecto SmartSantander y a un despliegue de sensores que, durante años, ha servido como laboratorio de ciudad conectada. Hoy el portal municipal sigue manteniendo una oferta amplia de servicios urbanos, movilidad, medio ambiente y participación, y conserva la huella de esa estrategia de ciudad sensorizada. La lección principal es que la ciudad puede actuar como plataforma experimental, pero las soluciones legadas tienden a fragmentar tráfico, ambiente y visualización si no evolucionan hacia un modelo de contexto unificado.

Fuentes: [Madrid aire de Madrid](https://airedemadrid.madrid.es/), [Madrid datos abiertos](https://datos.madrid.es/), [Barcelona portal municipal](https://www.barcelona.cat/), [Santander portal municipal](https://www.santander.es/), [SmartSantander](https://www.smartsantander.eu/).

## 3. Literatura académica reciente

La literatura reciente converge en cinco patrones:

1. El tráfico rodado sigue siendo uno de los predictores más robustos de NO2 en entornos urbanos densos.
2. La relación tráfico-contaminación se modela cada vez más con enfoques espacio-temporales, combinando series temporales, redes neuronales, modelos estadísticos y variables meteorológicas.
3. El forecast urbano mejora cuando se incorporan variables de movilidad, no sólo emisiones o meteorología.
4. Los estudios más útiles para la gestión pública son los que identifican hotspots, horas punta y efectos de medidas de restricción o desvío.
5. La tendencia actual es unir medición local, datos satelitales y modelos de predicción para obtener una visión multiescala.

Para un documento de proyecto, lo más valioso no es citar una única técnica, sino mostrar que el consenso científico apoya la correlación entre intensidad de tráfico, calidad del aire y, en menor medida, exposición al ruido. UrbanPulse encaja precisamente ahí: no intenta demostrar que esa relación existe, sino operacionalizarla para una ciudad concreta.

## 4. Herramientas open source relevantes

El ecosistema open source ya ofrece piezas maduras, aunque dispersas:

- **FIWARE Orion-LD** para gestión de contexto NGSI-LD.
- **Smart Data Models** para esquemas interoperables de tráfico, ambiente y dispositivos.
- **QuantumLeap** y bases de series temporales para histórico y análisis.
- **Grafana** para visualización operativa y cuadros de mando.
- **OpenDataCam** para conteo de tráfico mediante visión artificial.
- **openair** para análisis de calidad del aire y exploración estadística.
- **Home Assistant** como ejemplo de integración abierta de sensores, aunque no esté orientado a escala urbana.

El patrón dominante es que cada pieza resuelve bien un bloque, pero pocas integran observación ambiental, tráfico y contexto urbano en un único plano semántico.

## 5. Limitaciones de las soluciones actuales

Las soluciones existentes comparten varios límites:

- El tráfico y la calidad del aire siguen normalmente en sistemas distintos.
- Las plataformas de ciudad suelen publicar indicadores, pero no causalidad ni correlación operativa.
- Los forecast regionales, como los de Copernicus, son valiosos pero demasiado gruesos para decisiones de calle o distrito.
- Muchas soluciones se orientan a grandes metrópolis y no al tamaño, coste y complejidad de una ciudad como A Coruña.
- La mayoría de dashboards muestran estado, pero no conectan sensores, dispositivos, observaciones y entidades de forma trazable.

## 6. Oportunidad para UrbanPulse A Coruña

UrbanPulse puede diferenciarse si asume cinco compromisos:

- integrar tráfico, calidad del aire y ruido en una misma capa de contexto;
- trabajar con NGSI-LD y Smart Data Models desde el diseño;
- producir analítica local y forecast accionable para ciudadanos y gestores;
- mantener una arquitectura abierta, modular y reutilizable;
- adaptar la solución al contexto atlántico y a la escala real de A Coruña.

En resumen, el estado del arte muestra que la base tecnológica existe, pero todavía falta una solución que conecte de forma nativa el flujo vehicular con el impacto ambiental y lo traduzca en decisiones urbanas locales. Ese es el espacio natural de UrbanPulse.
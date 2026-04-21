# Análisis Smart Data Models

Este documento resume el encaje semántico de las entidades FIWARE y Smart Data Models que sostienen el caso de uso de UrbanPulse A Coruña. El foco está en tres aspectos: atributos principales, distinción entre datos estáticos y dinámicos, y relaciones NGSI-LD entre entidades.

## 1. TrafficEnvironmentImpact

**Dominio:** Environment

**Propósito:** representar el impacto ambiental asociado a tráfico observado en una localización y periodo concretos.

**Atributos principales:**

- `id` y `type`: identidad de la entidad.
- `dateObservedFrom` y `dateObservedTo`: ventana temporal de observación.
- `location`: localización geoespacial de la observación.
- `source`, `dataProvider`, `name`, `description`: metadatos de origen y contexto.
- `traffic`: array de objetos que describen el impacto por clase de vehículo.
- En el interior de `traffic` aparecen valores como `averageVehicleSpeed`, `averageOccupancy`, `intensity` y `vehicleClass`.

**Estáticos vs dinámicos:**

- Estáticos o semiestáticos: `id`, `type`, `name`, `description`, `source`, `dataProvider`, estructura del modelo.
- Dinámicos IoT: `dateObservedFrom`, `dateObservedTo`, `location` si cambia el punto de observación, y los valores del array `traffic`.

**Relación NGSI-LD clave:**

- `traffic[].refTrafficFlowObserved` enlaza con una entidad `TrafficFlowObserved` concreta. Esa relación es la que materializa el vínculo entre el impacto ambiental y el flujo observado.

**Lectura funcional:**

No es un contador puro de tráfico; es una entidad de síntesis que asocia el flujo observado con impacto ambiental por clase de vehículo.

## 2. TrafficEnvironmentImpactForecast

**Dominio:** Environment

**Propósito:** forecast del impacto ambiental del tráfico, usando expectativas de flujo y comportamiento por clase de vehículo.

**Atributos principales:**

- `id`, `type`, `location`, `name`, `description`, `source`, `dataProvider`.
- `dateCreated`, `dateModified`, `dateIssued`: trazabilidad del ciclo de vida.
- `validFrom`, `validTo`, `validity`: ventana de validez del forecast.
- `traffic`: valores esperados de `averageVehicleSpeedExpected`, `intensityExpected`, `occupancyExpected`, `vehicleClass`.
- Variables de impacto previstas, como concentraciones esperadas de contaminantes.

**Estáticos vs dinámicos:**

- Estáticos o semiestáticos: identificador, metadatos, estructura del forecast.
- Dinámicos: todos los campos de predicción y especialmente las ventanas temporales de validez.

**Relación NGSI-LD clave:**

- El modelo no depende de una relación única explícita del tipo `refTrafficFlowObserved` en el mismo sentido que la entidad de impacto observado, pero conceptualmente reutiliza el mismo patrón de tráfico por clase de vehículo y se alimenta de observaciones similares.

**Lectura funcional:**

Es la versión predictiva del impacto ambiental y permite pasar de observación histórica a planificación anticipada.

## 3. TrafficFlowObserved

**Dominio:** Transportation

**Propósito:** medir el flujo vehicular observado en un segmento o punto del viario durante un intervalo.

**Atributos principales:**

- `id`, `type`, `dateObserved`, `dateObservedFrom`, `dateObservedTo`.
- `location`: normalmente `LineString` o geometría equivalente para el tramo observado.
- `laneId`, `laneDirection`: identificación y sentido del carril o tramo.
- `intensity`: número total de vehículos.
- `occupancy`: fracción de tiempo ocupada.
- `averageSpeed`, `maxSpeed`, `minSpeed`, `vehicleCount` o métricas análogas según versión.
- `reversedLane` o equivalente, si el modelo contempla reversión de carril.
- `refRoadSegment`: relación al segmento vial observado cuando existe la entidad de carretera.

**Estáticos vs dinámicos:**

- Estáticos o semiestáticos: `laneId`, `laneDirection`, `refRoadSegment`, parte de la geometría si el tramo es fijo.
- Dinámicos IoT: `dateObserved`, `intensity`, `occupancy`, `averageSpeed`, `maxSpeed`, `minSpeed`.

**Relaciones NGSI-LD relevantes:**

- `refRoadSegment` enlaza con la infraestructura viaria.
- `refDevice` puede vincular el observador con el dispositivo físico si el modelo o la instancia lo utiliza.

**Lectura funcional:**

Es la fuente primaria para cuantificar tráfico. No incorpora por sí sola el impacto ambiental, pero es el insumo base para derivarlo.

## 4. ItemFlowObserved

**Dominio:** Transportation

**Propósito:** generalizar la observación de flujos más allá de vehículos, permitiendo personas, barcos, aviones u otros ítems.

**Atributos principales:**

- `id`, `type`, `dateObserved`, `dateObservedFrom`, `dateObservedTo`.
- `location`: geometría del punto o tramo observado.
- `laneId`, `laneDirection`, `reverseLane`.
- `intensity`: número de ítems detectados.
- `averageSpeed`, `maxSpeed`, `minSpeed`, `averageLength`, `occupancy`, `congested`.
- `itemType`, `itemSubType`: tipología genérica del objeto observado.
- `refDevice`: relación con el dispositivo de captura.
- `refRoadSegment`: relación con el segmento vial o trazado asociado.

**Estáticos vs dinámicos:**

- Estáticos o semiestáticos: `itemType`, `itemSubType`, `laneId`, `laneDirection`, `refRoadSegment`.
- Dinámicos IoT: `dateObserved`, `intensity`, `speed`, `occupancy`, `congested`, `averageLength`.

**Relaciones NGSI-LD relevantes:**

- `refDevice` enlaza con la entidad `Device` que captura la medición.
- `refRoadSegment` enlaza con la infraestructura vial o de recorrido.

**Lectura funcional:**

Es el modelo más flexible para capturar flujos multimodales. UrbanPulse lo puede usar para tráfico rodado, movilidad blanda o incluso contextos portuarios si el caso de uso crece.

## 5. Device

**Dominio:** Device

**Propósito:** describir el dispositivo físico desplegado en campo.

**Atributos principales:**

- `id`, `type`.
- `category`, `controlledProperty`, `brandName`, `modelName`, `manufacturerName`.
- `serialNumber`, `softwareVersion`, `firmwareVersion`, `hardwareVersion`.
- `dateInstalled`, `dateFirstUsed`, `dateLastCalibration`, `dateLastValueReported`, `dateManufactured`.
- `deviceState`, `rssi`, `direction`, `distance`, `location`, `supportedProtocol`, `supportedUnits`.
- `refDeviceModel`: relación con el modelo de dispositivo.

**Estáticos vs dinámicos:**

- Estáticos: `brandName`, `modelName`, `manufacturerName`, `serialNumber`, `category`, `controlledProperty`, `refDeviceModel`.
- Dinámicos o de operación: `deviceState`, `dateLastValueReported`, `rssi`, `dateLastCalibration`, `location` si el equipo es móvil.

**Relación NGSI-LD clave:**

- `refDeviceModel` vincula el dispositivo con su diseño o plantilla técnica.

**Lectura funcional:**

Es la entidad que separa claramente el activo físico de la medición. UrbanPulse la necesita para trazabilidad, mantenimiento y gobierno del inventario IoT.

## 6. AirQualityObserved

**Dominio:** Environment

**Propósito:** representar una observación puntual o intervalar de calidad del aire en un lugar y tiempo concretos.

**Atributos principales:**

- `id`, `type`, `dateObserved`, `location`.
- `airQualityIndex`, `airQualityLevel`.
- Contaminantes como `no`, `no2`, `nox`, `o3`, `so2`, `co`, `co2`, `pm10`, `pm25`, `tsp`, `tpc`, `voc`, `temperature`, `pressure`, `humidity`, `windSpeed`, `windDirection`.
- `areaServed`, `name`, `description`, `source`, `dataProvider`.
- `refDevice`, `refPointOfInterest`, `refWeatherObserved`.

**Estáticos vs dinámicos:**

- Estáticos o semiestáticos: `areaServed`, `name`, `description`, relaciones de contexto, metadatos.
- Dinámicos IoT: `dateObserved`, contaminantes, meteorología local y `airQualityIndex`.

**Relaciones NGSI-LD relevantes:**

- `refDevice` enlaza con el sensor o estación que captura la observación.
- `refPointOfInterest` enlaza con la estación o punto de interés.
- `refWeatherObserved` añade el contexto meteorológico asociado.

**Lectura funcional:**

Es el ancla ambiental principal del escenario. Complementa tráfico con evidencia directa de contaminación y contexto meteorológico.

## 7. NoiseLevelObserved

**Dominio:** Environment

**Propósito:** representar niveles de ruido observados en una localización y periodo.

**Atributos principales:**

- `id`, `type`, `dateObservedFrom`, `dateObservedTo`, `location`.
- `LAS`, `LAeq`, `LAeq_d`, `LAmax`.
- `distanceAverage`, `heightAverage`, `obstacles`, `sonometerClass`.
- `name`, `description`, `source`, `dataProvider`.
- `refDevice`, `refPointOfInterest`, `refWeatherObserved`.

**Estáticos vs dinámicos:**

- Estáticos o semiestáticos: `sonometerClass`, `obstacles`, `distanceAverage`, `heightAverage`.
- Dinámicos IoT: ventanas temporales y métricas acústicas.

**Relaciones NGSI-LD relevantes:**

- `refDevice` enlaza con el sonómetro o sensor acústico.
- `refPointOfInterest` y `refWeatherObserved` contextualizan la medición.

**Lectura funcional:**

Es clave para capturar un impacto urbano frecuentemente correlacionado con tráfico, pero ignorado por muchas soluciones centradas sólo en aire.

## 8. Relaciones cruzadas del escenario

La lógica funcional recomendada para UrbanPulse es esta:

- `Device` describe el activo físico.
- `TrafficFlowObserved` o `ItemFlowObserved` describen el flujo observado.
- `TrafficEnvironmentImpact` agrega la lectura de impacto y se enlaza con el flujo mediante `refTrafficFlowObserved`.
- `TrafficEnvironmentImpactForecast` proyecta el impacto esperado a futuro.
- `AirQualityObserved` y `NoiseLevelObserved` dan el estado ambiental directo que valida o contrasta el efecto del tráfico.

## 9. Complementariedad transversal

Los modelos de tráfico aportan causa o correlato operativo. Los de ambiente aportan efecto medido. `Device` aporta trazabilidad, gobernanza y mantenimiento. Juntos permiten un grafo semántico completo para analítica urbana: qué pasó, dónde, cuándo, con qué sensor, sobre qué tramo y con qué impacto ambiental.

## 10. Conclusión

La fortaleza de Smart Data Models no está en una entidad aislada, sino en la composición. UrbanPulse A Coruña puede construir un sistema coherente si usa los modelos de tráfico como entrada, los de ambiente como resultado y `Device` como capa de trazabilidad. Esa combinación permite observación, explicación y forecast en una misma arquitectura NGSI-LD.
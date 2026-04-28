/* ===================================
   VIEWER3D.JS - ThreeJS 3D immersive viewer
   =================================== */

import { getSensorHistory, getSensors } from './api.js';
import { on as wsOn } from './websocket.js';

const CORUNA_CENTER = { lat: 43.3713, lon: -8.4194 };
let scene, camera, renderer;
let pollutionCloud = null;
let buildings = [];
let sensorMarkers = [];
let isTimeLapseRunning = false;
let timeLapseData = [];
let currentTimeLapseIndex = 0;

/**
 * Initialize ThreeJS 3D viewer
 */
export async function initializeViewer3D() {
    const container = document.getElementById('canvas-3d');
    if (!container) return;

    if (typeof THREE === 'undefined') {
        container.innerHTML = `
            <div style="height: 100%; display: flex; align-items: center; justify-content: center; color: #cbd5e1; background: #0a0e27; border: 1px solid #2d3748; border-radius: 12px; padding: 24px; text-align: center;">
                <div>
                    <h3 style="margin: 0 0 8px 0; color: #00d4ff;">Visor 3D no disponible</h3>
                    <p style="margin: 0;">Three.js no se cargó en este navegador. La aplicación sigue funcionando sin la vista 3D.</p>
                </div>
            </div>
        `;
        return;
    }

    ensureTweenShim();

    // Scene setup
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0e27);
    scene.fog = new THREE.Fog(0x0a0e27, 1000, 5000);

    // Camera setup
    const width = container.clientWidth;
    const height = container.clientHeight;
    camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 10000);
    camera.position.set(0, 500, 800);
    camera.lookAt(0, 0, 0);

    // Renderer setup
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    // Lighting
    setupLighting();

    // Create buildings
    await createBuildings();

    // Create volumetric pollution cloud
    createPollutionCloud();

    // Create sensor markers
    await createSensorMarkers();

    // Setup controls
    setupControls();

    // Setup event listeners
    setupEventListeners();

    // Load time-lapse data
    await loadTimeLapseData();

    // Handle window resize
    window.addEventListener('resize', onWindowResize);

    // Start animation loop
    animate();
}

/**
 * Setup lighting
 */
function setupLighting() {
    // Ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    // Directional light (sun)
    const sunLight = new THREE.DirectionalLight(0xffffff, 0.8);
    sunLight.position.set(500, 1000, 500);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 2048;
    sunLight.shadow.mapSize.height = 2048;
    sunLight.shadow.camera.left = -1500;
    sunLight.shadow.camera.right = 1500;
    sunLight.shadow.camera.top = 1500;
    sunLight.shadow.camera.bottom = -1500;
    scene.add(sunLight);

    // Hemisphere light
    const hemiLight = new THREE.HemisphereLight(0x87ceeb, 0x000000, 0.4);
    scene.add(hemiLight);
}

/**
 * Create buildings from procedural geometry
 */
async function createBuildings() {
    // Create a grid of buildings representing city blocks
    const buildingGroup = new THREE.Group();
    
    // Create a 10x10 grid of buildings centered on Coruna
    const gridSize = 10;
    const spacing = 100;
    const baseX = -(gridSize * spacing) / 2;
    const baseZ = -(gridSize * spacing) / 2;

    for (let i = 0; i < gridSize; i++) {
        for (let j = 0; j < gridSize; j++) {
            const x = baseX + i * spacing + (Math.random() - 0.5) * spacing * 0.4;
            const z = baseZ + j * spacing + (Math.random() - 0.5) * spacing * 0.4;
            
            // Random building height (20-200 meters, scaled down for visualization)
            const height = 20 + Math.random() * 180;
            const width = 40 + Math.random() * 40;
            const depth = 40 + Math.random() * 40;

            const geometry = new THREE.BoxGeometry(width, height, depth);
            
            // Material with subtle color variation
            const hue = 0.6 + (Math.random() - 0.5) * 0.1;
            const material = new THREE.MeshStandardMaterial({
                color: new THREE.Color().setHSL(hue, 0.3, 0.4),
                metalness: 0.2,
                roughness: 0.8,
            });

            const building = new THREE.Mesh(geometry, material);
            building.position.set(x, height / 2, z);
            building.castShadow = true;
            building.receiveShadow = true;
            
            buildingGroup.add(building);
            buildings.push(building);
        }
    }

    scene.add(buildingGroup);

    // Add ground plane
    const groundGeometry = new THREE.PlaneGeometry(2000, 2000);
    const groundMaterial = new THREE.MeshStandardMaterial({
        color: 0x2a3f2f,
        metalness: 0.1,
        roughness: 0.9,
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);
}

/**
 * Create volumetric pollution cloud
 */
function createPollutionCloud() {
    // Create particle system for pollution cloud
    const particleCount = 2000;
    const geometry = new THREE.BufferGeometry();
    
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
        positions[i * 3] = (Math.random() - 0.5) * 800;
        positions[i * 3 + 1] = Math.random() * 400;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 800;

        // Color: green to red gradient
        const intensity = Math.random();
        colors[i * 3] = intensity;      // Red
        colors[i * 3 + 1] = 1 - intensity;  // Green
        colors[i * 3 + 2] = 0;          // Blue

        sizes[i] = 10 + Math.random() * 20;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    const material = new THREE.PointsMaterial({
        size: 15,
        sizeAttenuation: true,
        vertexColors: true,
        transparent: true,
        opacity: 0.3,
    });

    pollutionCloud = new THREE.Points(geometry, material);
    scene.add(pollutionCloud);
}

/**
 * Create sensor location markers
 */
async function createSensorMarkers() {
    try {
        const sensorsData = await getSensors();
        
        sensorsData.forEach(sensorState => {
            const sensor = sensorState.sensor;
            
            // Create marker sphere
            const geometry = new THREE.SphereGeometry(30, 16, 16);
            const material = new THREE.MeshStandardMaterial({
                color: 0x00d4ff,
                emissive: 0x00d4ff,
                emissiveIntensity: 0.3,
                metalness: 0.5,
                roughness: 0.5,
            });

            const marker = new THREE.Mesh(geometry, material);
            
            // Position based on lat/lon (simplified projection)
            const x = (sensor.lon - CORUNA_CENTER.lon) * 10000;
            const z = (sensor.lat - CORUNA_CENTER.lat) * 10000;
            marker.position.set(x, 100, z);

            marker.castShadow = true;
            marker.receiveShadow = true;
            marker.userData = { sensorId: sensor.id, sensorName: sensor.name };

            scene.add(marker);
            sensorMarkers.push(marker);

            // Add glow animation
            new TWEEN.Tween(marker.position)
                .to({ y: 150 }, 2000)
                .easing(TWEEN.Easing.Sinusoidal.InOut)
                .repeat(Infinity)
                .start();
        });

    } catch (error) {
        console.error('Error creating sensor markers:', error);
    }
}

/**
 * Setup camera controls (orbit + zoom)
 */
function setupControls() {
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    let rotation = { x: 0, y: 0 };

    document.addEventListener('mousedown', (e) => {
        isDragging = true;
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            const deltaX = e.clientX - previousMousePosition.x;
            const deltaY = e.clientY - previousMousePosition.y;

            rotation.y += deltaX * 0.01;
            rotation.x += deltaY * 0.01;

            previousMousePosition = { x: e.clientX, y: e.clientY };
        }
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
    });

    document.addEventListener('wheel', (e) => {
        e.preventDefault();
        const speed = 50;
        camera.position.z += e.deltaY > 0 ? speed : -speed;
        camera.position.z = Math.max(300, Math.min(2000, camera.position.z));
    });

    // Touch controls
    let touchStart = { x: 0, y: 0 };
    document.addEventListener('touchstart', (e) => {
        touchStart = { x: e.touches[0].clientX, y: e.touches[0].clientY };
    });

    document.addEventListener('touchmove', (e) => {
        if (e.touches.length === 1) {
            const deltaX = e.touches[0].clientX - touchStart.x;
            const deltaY = e.touches[0].clientY - touchStart.y;

            rotation.y += deltaX * 0.01;
            rotation.x += deltaY * 0.01;
        } else if (e.touches.length === 2) {
            // Pinch zoom
            const dist = Math.hypot(
                e.touches[0].clientX - e.touches[1].clientX,
                e.touches[0].clientY - e.touches[1].clientY
            );
            // Zoom logic here
        }
    });

    // Store rotation for animation loop
    scene.userData.rotation = rotation;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Time-lapse button
    const timeLapseBtn = document.getElementById('btn-time-lapse');
    if (timeLapseBtn) {
        timeLapseBtn.addEventListener('click', toggleTimeLapse);
    }

    // Timeline slider
    const timelineSlider = document.getElementById('timeline-slider');
    if (timelineSlider) {
        timelineSlider.addEventListener('input', (e) => {
            const hour = parseInt(e.target.value);
            updatePollutionCloudForHour(hour);
            updateTimelineLabel(hour);
        });
    }

    // Listen to sensor updates
    wsOn('sensor_update', (data) => {
        updatePollutionCloudFromSensorData(data);
    });
}

/**
 * Load 24h historical data for time-lapse
 */
async function loadTimeLapseData() {
    try {
        const sensorsData = await getSensors();
        
        for (const sensorState of sensorsData.slice(0, 3)) {
            const sensorId = sensorState.sensor.id;
            const history = await getSensorHistory(sensorId, 24);
            
            if (!timeLapseData[sensorId]) {
                timeLapseData[sensorId] = [];
            }
            
            const airQualityData = history.AirQualityObserved || [];
            timeLapseData[sensorId] = airQualityData;
        }

    } catch (error) {
        console.error('Error loading time-lapse data:', error);
    }
}

/**
 * Update pollution cloud for specific hour
 */
function updatePollutionCloudForHour(hour) {
    if (!pollutionCloud) return;

    const positions = pollutionCloud.geometry.attributes.position.array;
    const colors = pollutionCloud.geometry.attributes.color.array;

    let averageIntensity = 0;
    let dataPointCount = 0;

    // Calculate average NO2 from historical data
    Object.values(timeLapseData).forEach(sensorData => {
        if (sensorData[hour]) {
            averageIntensity += sensorData[hour].no2 || 0;
            dataPointCount++;
        }
    });

    if (dataPointCount > 0) {
        averageIntensity /= dataPointCount;
    }

    // Update particle colors based on intensity
    const intensity = Math.min(averageIntensity / 150, 1.0);

    for (let i = 0; i < colors.length; i += 3) {
        colors[i] = intensity;           // Red
        colors[i + 1] = 1 - intensity;   // Green
        colors[i + 2] = 0;               // Blue
    }

    pollutionCloud.geometry.attributes.color.needsUpdate = true;
}

/**
 * Toggle time-lapse animation
 */
function toggleTimeLapse() {
    isTimeLapseRunning = !isTimeLapseRunning;
    const btn = document.getElementById('btn-time-lapse');
    if (btn) {
        btn.textContent = isTimeLapseRunning ? '⏸ Pausar' : '▶ Reproducir';
    }
}

/**
 * Update timeline label
 */
function updateTimelineLabel(hour) {
    const label = document.getElementById('timeline-label');
    if (label) {
        label.textContent = `${String(hour).padStart(2, '0')}:00`;
    }
}

/**
 * Update pollution cloud from real-time sensor data
 */
function updatePollutionCloudFromSensorData(data) {
    if (!pollutionCloud) return;

    const positions = pollutionCloud.geometry.attributes.position.array;
    const colors = pollutionCloud.geometry.attributes.color.array;

    const intensity = Math.min((data.no2 || 0) / 150, 1.0);

    // Update particle colors
    for (let i = 0; i < colors.length; i += 3) {
        colors[i] = Math.min(colors[i] + intensity * 0.01, intensity);
        colors[i + 1] = Math.max(colors[i + 1] - intensity * 0.01, 1 - intensity);
        colors[i + 2] = 0;
    }

    pollutionCloud.geometry.attributes.color.needsUpdate = true;
}

/**
 * Window resize handler
 */
function onWindowResize() {
    const container = document.getElementById('canvas-3d');
    if (!container || !camera || !renderer) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
}

function ensureTweenShim() {
    if (typeof window.TWEEN !== 'undefined' && typeof window.TWEEN.Tween === 'function') {
        return window.TWEEN;
    }

    class NoopTween {
        constructor() {}
        to() { return this; }
        easing() { return this; }
        repeat() { return this; }
        start() { return this; }
    }

    window.TWEEN = {
        Tween: NoopTween,
        Easing: {
            Sinusoidal: {
                InOut: (value) => value,
            },
        },
        update() {},
    };

    return window.TWEEN;
}

/**
 * Animation loop
 */
function animate() {
    requestAnimationFrame(animate);

    // Update camera rotation
    if (scene.userData.rotation) {
        const rotation = scene.userData.rotation;
        const radius = Math.hypot(camera.position.x, camera.position.z);
        camera.position.x = radius * Math.sin(rotation.y);
        camera.position.z = radius * Math.cos(rotation.y);
        camera.position.y = Math.max(100, Math.min(1000, camera.position.y - rotation.x * 100));
    }

    // Update time-lapse
    if (isTimeLapseRunning) {
        const timelineSlider = document.getElementById('timeline-slider');
        currentTimeLapseIndex = (currentTimeLapseIndex + 1) % 1440; // 24h * 60 min
        const hour = Math.floor(currentTimeLapseIndex / 60);
        
        if (timelineSlider) {
            timelineSlider.value = hour;
        }
        
        updatePollutionCloudForHour(hour);
        updateTimelineLabel(hour);
    }

    // Update sensor markers
    sensorMarkers.forEach(marker => {
        marker.rotation.x += 0.01;
        marker.rotation.y += 0.01;
    });

    // Rotate pollution cloud
    if (pollutionCloud) {
        pollutionCloud.rotation.y += 0.0001;
    }

    TWEEN.update();
    renderer.render(scene, camera);
}

export default {
    initializeViewer3D,
};

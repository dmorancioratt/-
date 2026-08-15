precision mediump float;

varying vec3 vPosition;

uniform float uSunAzimuth;
uniform float uSunElevation;
uniform vec3 uSunColor;
uniform vec3 uSkyColorLow;
uniform vec3 uSkyColorHigh;
uniform float uSunSize;
uniform float uTime;

float hash(vec3 p) {
    p = fract(p * 0.3183099 + 0.1);
    p *= 17.0;
    return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

float starField(vec3 dir) {
    float threshold = 0.998;
    float starValue = hash(normalize(dir) * 100.0);
    float twinkle = sin(uTime * 2.0 + hash(normalize(dir) * 50.0) * 6.28) * 0.3 + 0.7;
    if (starValue > threshold) {
        return (starValue - threshold) / (1.0 - threshold) * twinkle;
    }
    return 0.0;
}

void main() {
    float azimuth = radians(uSunAzimuth);
    float elevation = radians(uSunElevation);

    vec3 sunDirection = normalize(vec3(
        cos(elevation) * sin(azimuth),
        sin(elevation),
        cos(elevation) * cos(azimuth)
    ));

    vec3 direction = normalize(vPosition);

    float t = direction.y * 0.5 + 0.5;
    vec3 skyColor = mix(uSkyColorLow, uSkyColorHigh, t);

    float sunIntensity = pow(max(dot(direction, sunDirection), 0.0), 1000.0 / uSunSize);
    vec3 sunColor = uSunColor * sunIntensity;

    // Stars - visible in upper sky at night
    float nightFactor = 1.0 - smoothstep(-0.1, 0.3, sin(elevation));
    float starBrightness = starField(direction) * nightFactor;
    vec3 starColor = vec3(1.0, 0.95, 0.9) * starBrightness * 2.0;

    // Moon glow - a softer, cooler light opposite to sun when low
    float moonGlow = pow(max(dot(direction, -sunDirection + vec3(0.0, 0.5, 0.0)), 0.0), 8.0) * nightFactor * 0.3;
    vec3 moonColor = vec3(0.6, 0.7, 1.0) * moonGlow;

    vec3 color = skyColor + sunColor + starColor + moonColor;

    gl_FragColor = vec4(color, 1.0);
}

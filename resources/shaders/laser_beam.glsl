#version 330

#define PI 3.14159265


in vec2 fragCoord;
out vec4 fragColor;

uniform vec3 iResolution;
uniform float iTime;

// Controllable parameters
uniform vec3 iMouse;

uniform float radius_circle_a;
uniform float radius_circle_b;
uniform float radius_circle_c;
uniform float len_squer_a;
uniform float width_squer_a;
uniform float len_squer_b;
uniform float width_squer_b;
uniform float objectsOutlineWidth;
uniform float rayAngleControler;
uniform bool psychedelic;
uniform bool savePlayerPose;
uniform float objectAreaShade;

uniform bool dimerControler;
uniform float ringHue;
uniform float ringSaturation;
uniform float ringHueDelta;
uniform float shapeHue;
uniform float shapeHueDelta;

float distanceToCircle(vec2 p, vec2 center, float radius) {
    return length(p - center) - radius;
}

float distanceToBox(vec2 p, vec2 center, vec2 halfSize) {
    vec2 d = abs(p - center) - halfSize;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

float minDistance(float d, float distToObject){
    return min(d, distToObject);
}

float sceneDistance(vec2 p) {
    float d = 1e9; 
    d = min(d, distanceToCircle(p, vec2(-0.6,  0.4), radius_circle_a));
    d = min(d, distanceToCircle(p, vec2( 0.7, -0.5), radius_circle_b));
    d = min(d, distanceToCircle(p, vec2(-0.8, -0.55), radius_circle_c));
    d = min(d, distanceToBox(p, vec2(0.4,  0.1), vec2(len_squer_a, width_squer_a)));
    d = min(d, distanceToBox(p, vec2(0.9,  0.6), vec2(len_squer_b, width_squer_b)));
    return d;
}

// Returns the shape index (0-4) for the closest shape at point p
int getShapeIndex(vec2 p) {
    float d0 = distanceToCircle(p, vec2(-0.6,  0.4), radius_circle_a);
    float d1 = distanceToCircle(p, vec2( 0.7, -0.5), radius_circle_b);
    float d2 = distanceToCircle(p, vec2(-0.8, -0.55), radius_circle_c);
    float d3 = distanceToBox(p, vec2(0.4,  0.1), vec2(len_squer_a, width_squer_a));
    float d4 = distanceToBox(p, vec2(0.9,  0.6), vec2(len_squer_b, width_squer_b));
    
    float minDist = min(min(min(min(d0, d1), d2), d3), d4);
    
    if (abs(minDist - d0) < 0.001) return 0;
    if (abs(minDist - d1) < 0.001) return 1;
    if (abs(minDist - d2) < 0.001) return 2;
    if (abs(minDist - d3) < 0.001) return 3;
    return 4;
}

vec2 uvPos() {
    vec2 uv = fragCoord / iResolution.xy;
    uv = uv * 2.0 - 1.0;
    uv.x *= iResolution.x / iResolution.y;
    return uv;
}

void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
    float rayAngle = iTime;
    vec2 rayDir = normalize(vec2(cos(rayAngle), sin(rayAngle)));

    vec2 uv = uvPos();    
    vec3 color = vec3(0.02);

    vec2 rayOrigin = psychedelic ? uv : vec2(0.0);
    if(iMouse.z > 0.0){
        vec2 mousePos = iMouse.xy / iResolution.xy;
        mousePos = mousePos * 2.0 - 1.0;
        mousePos.x *= iResolution.x / iResolution.y;
        rayOrigin = mousePos;
    }


    const float COLOR_VALUE = 1.0;

    float distScene = sceneDistance(uv);
    float outline = smoothstep(0.008, 0.0, abs(distScene));
    
    // Calculate shape hue based on which shape is closest
    int shapeIdx = getShapeIndex(uv);
    float currentShapeHue = fract(shapeHue + float(shapeIdx) * shapeHueDelta);
    vec3 outlineColor = hsv2rgb(vec3(currentShapeHue, ringSaturation, COLOR_VALUE));
    color += outlineColor * outline * objectsOutlineWidth;
    
    vec3 areaColor = hsv2rgb(vec3(currentShapeHue, ringSaturation, COLOR_VALUE));
    color += step(distScene, 0.0) * areaColor * objectAreaShade;

    const float MAXCIRCLEDIST = 10;
    const float MAX_DIST = 3.0;
    const float EPSILON = 0.001;
    const int MAX_STEPS = 40;
    float travel = 0.0;
    float pixelSize = 1.5 / iResolution.y;

    vec2 hitPosition;
    bool hit = false;

    for (int step = 0; step < MAX_STEPS; step++) {
        vec2 currentPos = rayOrigin + rayDir * travel;
        float distToScene = sceneDistance(currentPos);

        float ring = abs(length(uv - currentPos) - distToScene);
        
        float dimer = 0.0;
        if (dimerControler == true) {
            dimer = sin(iTime * 10.0) * 0.5 + 1.5;
        }
        
        // Calculate HSV color for this ring - constant hue based on step
        float hue = fract(ringHue + float(step) * ringHueDelta);
        vec3 ringColor = hsv2rgb(vec3(hue, ringSaturation, COLOR_VALUE));
        
        float ringLine = smoothstep(pixelSize * 3.0, dimer, ring);
        color += ringColor * ringLine * 0.5;

        travel += distToScene;
        if (distToScene < EPSILON) { hit = true; hitPosition = currentPos; break; }
        if (travel > MAXCIRCLEDIST) break;
    }

    float distToRay = abs(dot(uv - rayOrigin, vec2(-rayDir.y, rayDir.x)));
    float along = dot(uv - rayOrigin, rayDir);
    if (along > 0.0 && (!hit || along < length(hitPosition - rayOrigin))) {
        float line = smoothstep(0.004, 0.0, distToRay);
        color += vec3(1.0) * line;
    }

    if (hit) {
        float glow = smoothstep(pixelSize * 6.0, 0.0, length(uv - hitPosition));
        color += vec3(1.0, 0.1, 0.1) * glow * 3.0;
    }

    color += vec3(1.0, 0.4, 0.6) * smoothstep(pixelSize * 3.0, 0.0, length(uv - rayOrigin));
    fragColor = vec4(color, 1.0);
}

void main()
{
    mainImage(fragColor, fragCoord);
}

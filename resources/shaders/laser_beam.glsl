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
uniform float lanth_squer_a;
uniform float wighth_squer_a;
uniform float lanth_squer_b;
uniform float wighth_squer_b;

uniform float rayAngleControler;

uniform float uvSpeed;
uniform bool move;
uniform bool psychedelic;
uniform vec2 myPlayerPos; 
uniform bool savePlayerPose;

float distanceToCircle(vec2 p, vec2 center, float radius) {
    return length(p - center) - radius;
}

float distanceToBox(vec2 p, vec2 center, vec2 halfSize) {
    vec2 d = abs(p - center) - halfSize;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

float minDistance(float d, float distToObject){
    return min(d, distToObject);
}

float sceneDistance(vec2 p) {
    float d = 1e9; 
    d = min(d, distanceToCircle(p, vec2(-0.6,  0.4), radius_circle_a));
    d = min(d, distanceToCircle(p, vec2( 0.7, -0.5), radius_circle_b));
    d = min(d, distanceToCircle(p, vec2(-0.8, -0.55), radius_circle_c));
    d = min(d, distanceToBox(p, vec2(0.4,  0.1), vec2(lanth_squer_a, wighth_squer_a)));
    d = min(d, distanceToBox(p, vec2(0.9,  0.6), vec2(lanth_squer_b, wighth_squer_b)));
    return d;
}

vec2 uvPos() {
    vec2 uv = fragCoord / iResolution.xy;
    uv = uv * 2.0 - 1.0;
    uv.x *= iResolution.x / iResolution.y;
    return uv  ;
}

vec2 playerPos(vec2 uv, float rayAngle){
    // float uvSpeed = 1;
    vec2 uvP = vec2 (0.0);
    if (psychedelic == true){
        uvP = uv;
    }
    uvP.x += (cos(rayAngle) * uvSpeed);
    uvP.y += (sin(rayAngle) * uvSpeed);

    // if (savePlayerPose == true){
    //     myPlayerPos = uvP;
    // }   
    // else{
    //     uvP = myPlayerPos;
    // }

    return uvP;
}

void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
    float rayAngle = rayAngleControler;
    vec2 rayDir = normalize(vec2(cos(rayAngle), sin(rayAngle)));

    vec2 uv = uvPos();    
    vec2 uvP = playerPos(uv, rayAngle);
    vec3 color = vec3(0.02);

    vec2 rayOrigin = vec2(uvP);
    if(iMouse.z > 0.0){
        vec2 mousePos = iMouse.xy / iResolution.xy;
        mousePos = mousePos * 2.0 - 1.0;
        mousePos.x *= iResolution.x / iResolution.y;
        rayOrigin = mousePos;
    }


    float distScene = sceneDistance(uv);
    float outline = smoothstep(0.008, 0.0, abs(distScene));
    color += vec3(0.2) * outline;
    color += step(distScene, 0.0) * vec3(0.05);

    const int MAX_STEPS = 40;
    const float MAX_DIST = 3.0;
    const float EPSILON = 0.001;
    float travel = 0.0;
    float pixelSize = 1.5 / iResolution.y;

    vec2 hitPosition;
    bool hit = false;

    for (int step = 0; step < MAX_STEPS; step++) {
        vec2 currentPos = rayOrigin + rayDir * travel;
        float distToScene = sceneDistance(currentPos);

        float ring = abs(length(uv - currentPos) - distToScene);
        float ringLine = smoothstep(pixelSize * 3.0, 0.0, ring);
        color += vec3(0.8) * ringLine * 0.5;

        travel += distToScene;
        if (distToScene < EPSILON) { hit = true; hitPosition = currentPos; break; }
        if (travel > MAX_DIST) break;
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

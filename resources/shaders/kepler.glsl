#version 330

in vec2 fragCoord;
out vec4 fragColor;

// Controllable parameters for dynamic interaction
uniform vec3 iResolution;
uniform float iTime;
uniform vec4 iMouse = vec4(0.0, 0.0, 0.0, 0.0); // Mouse support (unused but for compatibility)

uniform float orbitSpeed = 0.125;      // Speed of planetary orbit
uniform float timeScale = 0.1;         // Overall time scaling
uniform float cameraDistance = 2.5;    // Distance from planet
uniform float atmosphereIntensity = 0.45;  // Atmosphere visibility
uniform float cloudDensity = 3.0;      // Cloud density multiplier
uniform float landContrast = 0.75;     // Land visibility contrast
uniform float starBrightness = 1.0;    // Star field brightness
uniform float surfaceDetail = 1.0;     // Surface detail level

/*--------------------------------------------------------------------------------------
License CC0 - http://creativecommons.org/publicdomain/zero/1.0/
To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
----------------------------------------------------------------------------------------
^ This means do ANYTHING YOU WANT with this code. Because we are programmers, not lawyers.
-Otavio Good
*/

float PI = 3.14159265;
vec3 sunCol = vec3(258.0, 208.0, 100.0) / 15.0;
vec3 environmentSphereColor = vec3(0.3001, 0.501, 0.901) * 0.0;

float distFromSphere;
vec3 normal;
vec3 texBlurry;

vec3 saturate(vec3 a)
{
    return clamp(a, 0.0, 1.0);
}
vec2 saturate(vec2 a)
{
    return clamp(a, 0.0, 1.0);
}
float saturate(float a)
{
    return clamp(a, 0.0, 1.0);
}

// Enhanced noise functions for better planet features
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i + vec2(0.0, 0.0)), 
                   hash(i + vec2(1.0, 0.0)), u.x),
               mix(hash(i + vec2(0.0, 1.0)), 
                   hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

// Fractal noise for more complex patterns
float fbm(vec2 p, int octaves) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    for (int i = 0; i < octaves; i++) {
        value += amplitude * noise(frequency * p);
        amplitude *= 0.5;
        frequency *= 2.0;
    }
    return value;
}

// Multi-octave noise with ridged characteristics for mountains
float ridgedNoise(vec2 p, int octaves) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    for (int i = 0; i < octaves; i++) {
        float n = abs(noise(frequency * p) * 2.0 - 1.0);
        n = 1.0 - n;
        value += amplitude * n;
        amplitude *= 0.5;
        frequency *= 2.0;
    }
    return value;
}

// Generate continent-like patterns with more realism
float continents(vec2 p) {
    // Large scale continent shapes
    float base = fbm(p * 0.3, 3);
    // Medium scale terrain features
    float terrain = fbm(p * 1.2, 4) * 0.4;
    // Small scale detail
    float detail = fbm(p * 4.0, 2) * 0.2;
    
    float land = base + terrain + detail;
    return smoothstep(0.4, 0.8, land);
}

// Generate realistic mountain ranges
float mountains(vec2 p) {
    return ridgedNoise(p * 2.0, 4) * 0.6;
}

// Generate forest/vegetation patterns
float vegetation(vec2 p) {
    float veg = fbm(p * 3.0, 3);
    return smoothstep(0.3, 0.9, veg);
}

// Generate desert patterns
float desert(vec2 p) {
    float sand = fbm(p * 2.5 + vec2(100.0), 3);
    return smoothstep(0.2, 0.7, sand);
}

// Generate cloud patterns with more variation
float clouds(vec2 p, float time) {
    vec2 cloudP1 = p + vec2(time * 0.05, sin(time * 0.03) * 0.1);
    vec2 cloudP2 = p + vec2(time * 0.08, cos(time * 0.04) * 0.15);
    
    float cloud1 = fbm(cloudP1 * 2.5, 4);
    float cloud2 = fbm(cloudP2 * 1.8, 3) * 0.7;
    
    return max(cloud1, cloud2);
}

// Generate star field matching original approach more closely
vec3 starField(vec3 dir, float time) {
    vec3 stars = vec3(0.0);
    float dense = 16.0;
    
    vec3 localRay = normalize(dir);
    localRay.x = localRay.x + 1.0 - time * 0.1;
    
    vec2 wrap = fract(localRay.xy * dense);
    vec4 rand = vec4(hash(floor(localRay.xy * dense) / dense), 
                     hash(floor(localRay.xy * dense) / dense + vec2(1.0)), 
                     hash(floor(localRay.xy * dense) / dense + vec2(2.0)), 
                     1.0);
    
    vec3 starColor = rand.xyz * 0.75 + 0.25;
    rand.xy = rand.xy * 2.0 - 1.0;
    vec2 center = vec2(0.5) + rand.xy * 0.9;
    
    float star = length(wrap - center);
    star = saturate(1.0 - star);
    
    float blink = hash(localRay.xy + time * 0.03);
    float cluster = 0.3;
    star = pow(star, 60.0 + saturate(rand.z - 0.0) * 250.0 * cluster);
    star *= blink;
    
    return starColor * star * cluster;
}

// Generate milky way background matching original more closely
vec3 milkyWay(vec3 dir) {
    vec3 localRay = normalize(dir);
    float milkyMask = saturate(0.25 - abs(localRay.x - 0.65));
    
    // Multiple scales of noise to simulate galaxy texture
    vec2 milkyCoord = localRay.yx * 1.5 + vec2(0.65, 0.3);
    vec3 milkyway = vec3(fbm(milkyCoord, 6));
    vec3 milkyLOD = vec3(fbm(milkyCoord, 3));
    vec3 milkyDetail = vec3(fbm(-localRay.yx * 8.0 + vec2(0.65, 0.3), 4));
    
    milkyway.xyz = milkyway.yxz;  // Swizzle to match original
    milkyLOD.xyz = milkyLOD.yxz;
    
    milkyway *= milkyDetail.xxx;
    milkyway *= vec3(1.0, 0.8, 0.91) * 1.5;
    milkyway = pow(milkyway, vec3(6.0));  // Enhanced contrast
    milkyway += vec3(0.2, 0.0015, 1.001) * milkyLOD * 0.006;
    
    return milkyway;
}

vec3 GetSunColor(vec3 rayDir, vec3 sunDir)
{
    vec3 localRay = normalize(rayDir);
    float sunIntensity = 1.0 - (dot(localRay, sunDir) * 0.5 + 0.5);
    sunIntensity = 0.2 / sunIntensity;
    sunIntensity = min(sunIntensity, 40000.0);
    sunIntensity = max(0.0, sunIntensity - 3.0);

    // Generate enhanced star field
    vec3 stars = starField(localRay, iTime) * 12000.0 * starBrightness;
    
    // Generate enhanced milky way background
    vec3 milkyway = milkyWay(localRay) * 10850.0 * starBrightness;
    
    vec3 finalColor = milkyway + stars;
    finalColor += environmentSphereColor + sunCol * sunIntensity;
    return finalColor;
}

vec3 GetSunColorReflection(vec3 rayDir, vec3 sunDir)
{
    vec3 localRay = normalize(rayDir);
    float sunIntensity = 1.0 - (dot(localRay, sunDir) * 0.5 + 0.5);
    sunIntensity = 0.2 / sunIntensity;
    sunIntensity = min(sunIntensity, 40000.0);
    return environmentSphereColor + sunCol * sunIntensity;
}

float IntersectSphereAndRay(vec3 pos, float radius, vec3 posA, vec3 posB, out vec3 intersectA2, out vec3 intersectB2)
{
    vec3 eyeVec2 = normalize(posB - posA);
    float dp = dot(eyeVec2, pos - posA);
    vec3 pointOnLine = eyeVec2 * dp + posA;
    float distance = length(pointOnLine - pos);
    float ac = radius * radius - distance * distance;
    float rightLen = 0.0;
    if (ac >= 0.0) rightLen = sqrt(ac);
    intersectA2 = pointOnLine - eyeVec2 * rightLen;
    intersectB2 = pointOnLine + eyeVec2 * rightLen;
    distFromSphere = distance - radius;
    if (distance <= radius) return 1.0;
    return 0.0;
}

vec2 Spiral(vec2 uv)
{
    float reps = 2.0;
    vec2 uv2 = fract(uv * reps);
    vec2 center = floor(fract(uv * reps)) + 0.5;
    vec2 delta = uv2 - center;
    float dist = length(delta);
    vec2 offset = vec2(delta.y, -delta.x);
    float blend = clamp((0.5 - dist) * 2.0, 0.0, 1.0);
    blend = pow(blend, 1.5);
    offset *= clamp(blend, 0.0, 1.0);
    return uv + offset * vec2(1.0, 1.0) * 1.1 * texBlurry.x;
}

void main()
{
    vec2 uv = fragCoord.xy / iResolution.xy - 0.5;

    // Camera setup
    vec3 camUp = vec3(0, 1, 0);
    vec3 camLookat = vec3(0, 0.0, 0);
    
    float mx = -PI / 2.0;
    float my = 0.0;
    vec3 camPos = vec3(cos(my) * cos(mx), sin(my), cos(my) * sin(mx)) * cameraDistance;

    vec3 camVec = normalize(camLookat - camPos);
    vec3 sideNorm = normalize(cross(camUp, camVec));
    vec3 upNorm = cross(camVec, sideNorm);
    vec3 worldFacing = (camPos + camVec);
    vec3 worldPix = worldFacing + uv.x * sideNorm * (iResolution.x / iResolution.y) + uv.y * upNorm;
    vec3 relVec = normalize(worldPix - camPos);

    vec3 planetPos = vec3(0.0, 0.0, 0.0);
    vec3 iA, iB, iA2, iB2;
    float t = iTime * timeScale + 0.7 - iMouse.x * 0.01; // Include mouse control like original
    float cloudT = iTime * timeScale;
    float distFromSphere2;
    vec3 normal2;
    
    float hit2 = IntersectSphereAndRay(planetPos, 1.05, camPos, worldPix, iA2, iB2);
    normal2 = normal;
    distFromSphere2 = distFromSphere;
    float hit = IntersectSphereAndRay(planetPos, 1.0, camPos, worldPix, iA, iB);
    normal = normalize(iA - planetPos);
    
    vec2 polar = vec2(atan(normal.x, normal.z), acos(normal.y));
    polar.x = (polar.x + PI) / (PI * 2.0);
    polar.y = polar.y / PI;
    polar.x = (polar.x + 2.03);
    polar.xy = iA.xy;

    // Generate detailed planetary surface features (restored detailed terrain)
    vec2 surfaceCoord = polar.xy + vec2(t, 0);
    
    // Generate multi-scale noise for realistic terrain
    vec4 texNoise = vec4(fbm(surfaceCoord * 2.0, 4),
                         fbm(surfaceCoord * 1.0, 3),
                         fbm(surfaceCoord * 4.0, 5),
                         1.0);
    texBlurry = vec3(fbm(surfaceCoord * 0.03125 * 0.25 * surfaceDetail, 2));

    // Generate detailed terrain types for realistic planet surface
    float continentMask = continents(surfaceCoord * surfaceDetail);
    float mountainMask = mountains(surfaceCoord * surfaceDetail);
    float vegetationMask = vegetation(surfaceCoord * surfaceDetail);
    float desertMask = desert(surfaceCoord * surfaceDetail);

    // Generate base terrain texture (matching original approach but with our enhancements)
    vec3 tex = vec3(continentMask);
    tex *= tex;
    
    // Flipped version for variety
    vec3 texFlip = vec3(continents(1.0 - surfaceCoord * 0.5 * surfaceDetail));
    texFlip *= texFlip;

    // Enhanced cloud layers with movement (keep our improved clouds)
    vec3 texS = vec3(clouds(Spiral(surfaceCoord), cloudT));
    texS *= texS;
    vec3 texFlipS = vec3(clouds(1.0 - Spiral(surfaceCoord), cloudT));
    texFlipS *= texFlipS;

    float atmosphereDensity = (1.45 + normal.z);
    vec3 atmosphereColor = vec3(0.075, 0.35, 0.99) * atmosphereIntensity;
    float cloudDensityCalc = max(0.0, (pow(texFlipS.x * texS.x, 0.7) * cloudDensity));
    vec3 finalAtmosphere = atmosphereColor * atmosphereDensity + cloudDensityCalc;
    vec3 finalColor = finalAtmosphere;

    // Generate detail map and land elevation (enhanced approach)
    vec3 detailMap = vec3(fbm(surfaceCoord * 2.0, 4)) * 0.5 + 0.5;
    
    // Generate land using multiple elevation sources
    float elevationNoise = fbm(surfaceCoord * 0.25, 4);
    float land = pow(max(0.0, elevationNoise - 0.25), 0.4) * landContrast;
    float land2 = land * texBlurry.x * 6.0;
    
    // Apply terrain masks for realistic distribution
    land *= continentMask * detailMap.x;
    land2 = max(0.0, land2);
    
    // Ocean areas reduce land visibility
    land -= tex.x * 0.65;
    land = max(0.0, land);
    
    float iceFactor = abs(pow(normal.y, 2.0));
    
    // Restore detailed terrain coloring system
    vec3 deepOceanColor = vec3(0.0, 0.1, 0.3);
    vec3 shallowOceanColor = vec3(0.0, 0.2, 0.5);
    vec3 beachColor = vec3(0.8, 0.7, 0.5);
    vec3 grassColor = vec3(0.1, 0.6, 0.2);
    vec3 forestColor = vec3(0.05, 0.4, 0.1);
    vec3 mountainColor = vec3(0.4, 0.3, 0.2);
    vec3 desertColor = vec3(0.7, 0.5, 0.3);
    vec3 snowColor = vec3(0.9, 0.95, 1.0);
    
    // Start with ocean base
    vec3 terrainColor = mix(deepOceanColor, shallowOceanColor, 
                           smoothstep(0.0, 0.3, continentMask));
    
    // Add beaches at coastlines
    float coastline = smoothstep(0.2, 0.4, continentMask) - smoothstep(0.4, 0.6, continentMask);
    terrainColor = mix(terrainColor, beachColor, coastline * 0.8);
    
    // Add detailed land areas
    float landMask = smoothstep(0.4, 0.7, continentMask);
    vec3 landColor = grassColor;
    
    // Forest areas (vegetation in suitable regions)
    landColor = mix(landColor, forestColor, vegetationMask * landMask * 0.8);
    
    // Desert areas (arid regions)
    landColor = mix(landColor, desertColor, desertMask * landMask * (1.0 - vegetationMask * 0.5));
    
    // Mountain areas (high elevation)
    landColor = mix(landColor, mountainColor, mountainMask * landMask * 0.7);
    
    // Apply land to terrain
    terrainColor = mix(terrainColor, landColor, landMask);
    
    // Apply detail variations and original-style land coloring blend
    vec3 originalStyleLand = max(vec3(0.0), vec3(0.13, 0.65, 0.01) * land) + 
                             max(vec3(0.0), vec3(0.8, 0.4, 0.01) * land2);
    
    // Blend our detailed terrain with original-style land coloring
    terrainColor = mix(terrainColor, originalStyleLand, 0.3);
    terrainColor *= (detailMap * 0.3 + 0.85);
    
    // Ice caps at poles
    vec3 finalLand = mix(terrainColor, snowColor, iceFactor * 0.6);
    finalLand = mix(atmosphereColor * 0.05, finalLand, 
                   pow(min(1.0, max(0.0, -distFromSphere * 1.0)), 0.2));
    finalColor += finalLand;
    finalColor *= hit;

    float refNoise = (texNoise.x + texNoise.y + texNoise.z) * 0.3333;
    vec3 noiseNormal = normal;
    noiseNormal.x += refNoise * 0.05 * hit;
    noiseNormal.y += tex.x * hit * 0.1;
    noiseNormal.z += texFlip.x * hit * 0.1;
    noiseNormal = normalize(noiseNormal);
    vec3 ref = reflect(normalize(worldPix - camPos), noiseNormal);

    refNoise = refNoise * 0.25 + 0.75;
    vec3 sunDir = normalize(vec3(-0.009 + sin(iTime * orbitSpeed), -0.13, -cos(iTime * orbitSpeed)));
    vec3 r = normalize(cross(sunDir, vec3(0.0, 1.0, 0.0)));
    vec3 up = normalize(cross(sunDir, r));
    float binarySpeed = 0.5;
    float binaryDist = 0.3;
    sunDir += r * sin(iTime * binarySpeed) * binaryDist + up * cos(iTime * binarySpeed) * binaryDist;
    sunDir = normalize(sunDir);

    vec3 sunDir2 = normalize(vec3(-0.009 + sin((iTime + 0.2) * orbitSpeed), 0.13, -cos((iTime + 0.2) * orbitSpeed)));
    r = normalize(cross(sunDir2, vec3(0.0, 1.0, 0.0)));
    up = normalize(cross(sunDir2, r));
    sunDir2 -= r * sin(iTime * binarySpeed) * binaryDist + up * cos(iTime * binarySpeed) * binaryDist;
    sunDir2 = normalize(sunDir2);

    vec3 refNorm = normalize(ref);
    float glance = saturate(dot(refNorm, sunDir) * saturate(sunDir.z - 0.65));
    float glance2 = saturate(dot(refNorm, sunDir2) * saturate(sunDir2.z - 0.65));
    float reflectionMask = finalLand.x + finalLand.y * 1.5;
    vec3 sunRef = GetSunColorReflection(refNorm, sunDir) * 0.005 * hit * (1.0 - saturate(reflectionMask * 3.5)) * (1.0 - texS.x) * refNoise;
    vec3 sunRef2 = GetSunColorReflection(refNorm, sunDir2) * 0.005 * hit * (1.0 - saturate(reflectionMask * 3.5)) * (1.0 - texS.x) * refNoise;
    
    sunRef = mix(sunRef, vec3(3.75, 0.8, 0.02) * hit, glance);
    sunRef2 = mix(sunRef2, vec3(3.75, 0.8, 0.02) * hit, glance2);
    finalColor += sunRef;
    finalColor += sunRef2;

    vec3 sunsColor = GetSunColor(normalize(ref), sunDir) * 0.000096 * (1.0 - hit) +
                     GetSunColor(normalize(ref), sunDir2) * 0.000096 * (1.0 - hit);

    float outerGlow = 1.0 - clamp(distFromSphere * 20.0, 0.0, 1.0);
    outerGlow = pow(outerGlow, 5.2);
    finalColor += (atmosphereColor + vec3(0.2, 0.2, 0.2)) * outerGlow * (1.0 - hit);
    
    float light = saturate(dot(sunDir, noiseNormal));
    light += saturate(dot(sunDir2, noiseNormal));
    finalColor *= light * 0.75 + 0.001;
    finalColor += sunsColor;

    float scattering, scattering2;
    if (hit2 == 1.0) scattering = distance(iA2, iB2);
    scattering2 = scattering;
    scattering *= pow(saturate(dot(relVec, sunDir) - 0.96), 2.0);
    scattering2 *= pow(saturate(dot(relVec, sunDir2) - 0.96), 2.0);
    scattering *= hit2 * (1.0 - hit);
    scattering2 *= hit2 * (1.0 - hit);
    scattering *= outerGlow;
    scattering2 *= outerGlow;
    finalColor += vec3(1.0, 0.25, 0.05) * scattering * 3060.0;
    finalColor += vec3(1.0, 0.25, 0.05) * scattering2 * 3060.0;

    fragColor = vec4(sqrt(finalColor), 1.0);
}
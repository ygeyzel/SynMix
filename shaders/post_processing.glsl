#version 330

in vec2 fragCoord;
out vec4 fragColor;

// Input texture from first pass
uniform sampler2D uTexture;

// Screen resolution
uniform vec3 iResolution;
uniform float iTime;

// Post-processing effect parameters
uniform bool uInvertColors;
uniform bool uInvertRed;
uniform bool uInvertGreen;
uniform bool uInvertBlue;
uniform bool uInvertHue;
uniform bool uInvertSaturation;
uniform bool uInvertValue;

uniform float uWavesX;
uniform float uWavesY;
//uniform bool uIsDisplayDVDLogo = false;
bool uIsDisplayDVDLogo = true;

#define PI 3.14159265359

// RGB to HSV conversion
vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

// HSV to RGB conversion
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

vec2 applyWaveDistortion(vec2 uv, float time) {
    float waveAmplitude = 0.03;
    float waveSpeed = 2.0;
    float waveY = sin(uv.x * uWavesY + time * waveSpeed) * waveAmplitude;
    float waveX = cos(uv.y * uWavesX + 0.7 + time * waveSpeed * 1.3) * waveAmplitude;

    if (abs(uWavesX) > 0.01) {
        uv.x += waveX;
    }
    if (abs(uWavesY) > 0.01) {
        uv.y += waveY;
    }
    return uv;
}

//=============<DVD>===============

// ==== ADDITIONS ====
float hash12(vec2 p) { // @Dave_Hoskins : https://www.shadertoy.com/view/4djSRW
    vec3 p3 = fract(vec3(p.xyx) * .1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

vec3 hsl2rgb(in vec3 c) {
    vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
    return c.z + c.y * (rgb - 0.5) * (1.0 - abs(2.0 * c.z - 1.0));
}
// ===================

float vmin(vec2 v) {
    return min(v.x, v.y);
}

float vmax(vec2 v) {
    return max(v.x, v.y);
}

float ellip(vec2 p, vec2 s) {
    float m = vmin(s);
    return (length(p / s) * m) - m;
}

float halfEllip(vec2 p, vec2 s) {
    p.x = max(0., p.x);
    float m = vmin(s);
    return (length(p / s) * m) - m;
}

float fBox(vec2 p, vec2 b) {
    return vmax(abs(p) - b);
}

float dvd_d(vec2 p) {
    float d = halfEllip(p, vec2(.8, .5));
    d = max(d, -p.x - .5);
    float d2 = halfEllip(p, vec2(.45, .3));
    d2 = max(d2, min(-p.y + .2, -p.x - .15));
    d = max(d, -d2);
    return d;
}

float dvd_v(vec2 p) {
    vec2 pp = p;
    p.y += .7;
    p.x = abs(p.x);
    vec2 a = normalize(vec2(1, -.55));
    float d = dot(p, a);
    float d2 = d + .3;
    p = pp;
    d = min(d, -p.y + .3);
    d2 = min(d2, -p.y + .5);
    d = max(d, -d2);
    d = max(d, abs(p.x + .3) - 1.1);
    return d;
}

float dvd_c(vec2 p) {
    p.y += .95;
    float d = ellip(p, vec2(1.8, .25));
    float d2 = ellip(p, vec2(.45, .09));
    d = max(d, -d2);
    return d;
}

float dvd(vec2 p) {
    p.y -= .345;
    p.x -= .035;
    p *= mat2(1, -.2, 0, 1);
    float d = dvd_v(p);
    d = min(d, dvd_c(p));
    p.x += 1.3;
    d = min(d, dvd_d(p));
    p.x -= 2.4;
    d = min(d, dvd_d(p));
    return d;
}

float range(float vmin, float vmax, float value) {
    return (value - vmin) / (vmax - vmin);
}

float rangec(float a, float b, float t) {
    return clamp(range(a, b, t), 0., 1.);
}

void drawHit(inout vec4 col, vec2 p, vec2 hitPos, float hitDist) {
    float d = length(p - hitPos);

    #ifdef DEBUG
    col = mix(col, vec4(0, 1, 1, 0), step(d, .1));
    return;
    #endif

    float wavefront = d - hitDist * 1.5;
    float freq = 2.;

    float ripple = sin((wavefront * freq) * PI * 2. - PI / 2.);

    float blend = smoothstep(3., 0., hitDist);
    blend *= smoothstep(.2, -.5, wavefront);
    blend *= rangec(-4., .0, wavefront);

    float height = (ripple * blend);
    col.a -= height * 1.9 / freq;
}

vec2 ref(vec2 p, vec2 planeNormal, float offset) {
    float t = dot(p, planeNormal) + offset;
    p -= (2. * t) * planeNormal;
    return p;
}

// Flip every second cell to create reflection
void flip(inout vec2 pos) {
    vec2 flip = mod(floor(pos), 2.);
    pos = abs(flip - mod(pos, 1.));
}

float stepSign(float a) {
    //return sign(a);
    return step(0., a) * 2. - 1.;
}

vec2 compassDir(vec2 p) {
    //return sign(p - sign(p) * vmin(abs(p))); // this caused problems on some GPUs
    vec2 a = vec2(stepSign(p.x), 0);
    vec2 b = vec2(0, stepSign(p.y));
    float s = stepSign(p.x - p.y) * stepSign(-p.x - p.y);
    return mix(a, b, s * .5 + .5);
}

vec2 calcHitPos(vec2 move, vec2 dir, vec2 size) {
    vec2 hitPos = mod(move, 1.);
    vec2 xCross = hitPos - hitPos.x / (size / size.x) * (dir / dir.x);
    vec2 yCross = hitPos - hitPos.y / (size / size.y) * (dir / dir.y);
    hitPos = max(xCross, yCross);
    hitPos += floor(move);
    return hitPos;
}

vec4 DVDFragShader(vec2 fragCoord, vec3 iResolution, float iTime)
{
    vec2 p = (-iResolution.xy + 2.0 * fragCoord) / iResolution.y;
    vec2 screenSize = vec2(iResolution.x / iResolution.y, 1.) * 2.;

    float t = iTime;
    vec2 dir = normalize(vec2(9., 16) * screenSize);
    vec2 move = dir * t / 1.5;
    float logoScale = .1;
    vec2 logoSize = vec2(2., .85) * logoScale * 1.;

    vec2 size = screenSize - logoSize * 2.;

    // Remap so (0,0) is bottom left, and (1,1) is top right
    move = move / size + .5;

    // Calculate the point we last crossed a cell boundry
    vec2 lastHitPos = calcHitPos(move, dir, size);
    vec4 col = vec4(1, 1, 1, 0);
    vec4 colFx = vec4(1, 1, 1, 0);
    vec4 colFy = vec4(1, 1, 1, 0);
    vec2 e = vec2(.8, 0) / iResolution.y;

    const int limit = 5;

    for (int i = 0; i < limit; i++) {
        vec2 hitPos = lastHitPos;

        if (i > 0) {
            // Nudge it before the boundry to find the previous hit point
            hitPos = calcHitPos(hitPos - .00001 / size, dir, size);
        }

        lastHitPos = hitPos;
    }

    // Flip every second cell to create reflection
    flip(move);

    // Remap back to screen space
    move = (move - .5) * size;

    // invert colours
    col.rgb = clamp(1. - col.rgb, vec3(0), vec3(1));
    col.rgb /= 3.;

    // dvd logo
    float d = dvd((p - move) / logoScale);
    d /= fwidth(d);
    d = 1. - clamp(d, 0., 1.);
    col.a = d;
    col.rgb = mix(col.rgb, vec3(1), d);

    // ADDITION : Pick color by last hit position
    col.rgb *= hsl2rgb(vec3(hash12(lastHitPos / size), 0.6, 0.5));

    // gamma
    col.rgb = pow(col.rgb, vec3(0.4545));
    return col;
}
//=============<\DVD>===============

void main() {
    vec2 uv = fragCoord.xy / iResolution.xy;

    float waveAmplitude = 0.01;
    float waveFrequency = 100.0;
    float waveSpeed = 2.0;
    float waveX = sin(uv.y * waveFrequency + iTime * waveSpeed) * waveAmplitude;
    float waveY = cos(uv.x * waveFrequency * 0.7 + iTime * waveSpeed * 1.3) * waveAmplitude;

    if (abs(uWavesX) > 0.01) {
        uv.x += waveX;
    }
    if (abs(uWavesY) > 0.01) {
        uv.y += waveY;
    }
    vec4 color = texture(uTexture, uv);

    // Color inversion effect (full RGB inversion)
    if (uInvertColors) {
        color.rgb = 1.0 - color.rgb;
    }

    // Individual RGB channel inversion effects
    if (uInvertRed) {
        color.r = 1.0 - color.r;
    }
    if (uInvertGreen) {
        color.g = 1.0 - color.g;
    }
    if (uInvertBlue) {
        color.b = 1.0 - color.b;
    }

    // HSV space inversion effects
    if (uInvertHue || uInvertSaturation || uInvertValue) {
        vec3 hsv = rgb2hsv(color.rgb);

        if (uInvertHue) {
            hsv.x = fract(hsv.x + 0.5); // Invert hue by adding 0.5 (180 degrees)
        }
        if (uInvertSaturation) {
            hsv.y = 1.0 - hsv.y;
        }
        if (uInvertValue) {
            hsv.z = 1.0 - hsv.z;
        }

        color.rgb = hsv2rgb(hsv);
    }

    uv = applyWaveDistortion(uv, iTime);

    if (uIsDisplayDVDLogo) {
        vec4 dvd = DVDFragShader(fragCoord, iResolution, iTime);
        color = mix(color, dvd, dvd.a);
    }

    fragColor = color;
}

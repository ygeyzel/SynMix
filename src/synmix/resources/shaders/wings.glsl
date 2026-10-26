#version 330
// @christinacoffin
// 2015-05-07: 1st version, need to optim and do some proper AA

// https://www.shadertoy.com/view/4l23zc

in vec2 fragCoord;
out vec4 fragColor;

uniform vec3 iResolution;
uniform float iTime;

uniform float xOffset;
uniform float yOffset;

uniform float hueShift;
uniform float hueRange;
uniform float saturation;
uniform float brightness;
uniform float wingsFactor;
uniform float flap;

uniform float rot0;
uniform float rot1;
uniform float rotWeight;

uniform float scaleX0;
uniform float scaleX1;
uniform float scaleY0;
uniform float scaleY1;
uniform float scaleXY;

// HSV to RGB conversion
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

vec3 JuliaFractal(vec2 c, vec2 c2, float animparam, float anim2) {
    vec2 z = c;

    float ci = 0.0;
    float mean = 0.0;

    for (int i = 0; i < 64; i++) {
        vec2 a = vec2(z.x, abs(z.y));

        float b = atan(a.y * (0.99 + animparam * 9.0), a.x + .110765432 + animparam);

        if (b > 0.0)
            b -= 6.303431307 + (animparam * 3.1513);

        z = vec2(log(length(a * (0.98899 - (animparam * 2.70 * anim2)))), b) + c2;

        if (i > 0)
            mean += length(z / a * b);

        mean += a.x - (b * 77.0 / length(a * b));

        mean = clamp(mean, 111.0, 99999.0);
    }

    mean /= 131.21;
    ci = 1.0 - fract(log2(.5 * log2(mean / (0.57891895 - abs(animparam * 141.0)))));

    // Convert to HSV color space
    float hue = fract(hueShift + ci * hueRange);
    float sat = saturation;
    float val = brightness * (.5 + .5 * cos(6.0 * ci));

    return hsv2rgb(vec3(hue, sat, val));
}

void main() {
    float animWings = 0.004 * cos(iTime * wingsFactor);
    float animFlap = flap * sin(iTime * 1.0);
    float timeVal = 56.48 - 20.1601;
    vec2 uv = fragCoord.xy - iResolution.xy * .5;
    uv /= iResolution.x * 1.5113 * abs(sin(timeVal));
    uv.y -= animWings * 5.0;
    vec2 tuv = uv * 125.0;

    float rot = 3.141592654 * 0.5 + mix(rot0, rot1, sin(iTime) * rotWeight);
    float scaleX = mix(scaleX0, scaleX1, sin(iTime));
    float scaleY = mix(scaleY0, scaleY1, sin(iTime));

    tuv.x *= scaleX;
    tuv.y *= scaleY;
    tuv *= scaleXY;

    uv.x = tuv.x * cos(rot) - tuv.y * sin(rot);
    uv.y = 1.05 * tuv.x * sin(rot) + tuv.y * cos(rot);
    float juliax = tan(timeVal) * 0.011 + 0.02 / (fragCoord.y * 0.19531 * (1.0 - animFlap)) + xOffset;
    float juliay = cos(timeVal * 0.213) * (0.022 + animFlap) + 5.66752 - (juliax * 1.5101) + yOffset;

    float tapU = (1.0 / float(iResolution.x)) * 25.5 * cos(animFlap);
    float tapV = (1.0 / float(iResolution.y)) * 25.5 * cos(animFlap);

    fragColor = vec4(JuliaFractal(uv + vec2(0.0, 0.0), vec2(juliax, juliay), animWings, animFlap), 1.0);

    fragColor += vec4(JuliaFractal(uv + vec2(tapU, tapV), vec2(juliax, juliay), animWings, animFlap), 1.0);
    fragColor += vec4(JuliaFractal(uv + vec2(tapU, -tapV), vec2(juliax, juliay), animWings, animFlap), 1.0);
    fragColor += vec4(JuliaFractal(uv + vec2(-tapU, tapV), vec2(juliax, juliay), animWings, animFlap), 1.0);
    fragColor += vec4(JuliaFractal(uv + vec2(-tapU, -tapV), vec2(juliax, juliay), animWings, animFlap), 1.0);

    fragColor.xyz = fragColor.zyx;
    fragColor.xyz = vec3(1) - fragColor.xyz;
}

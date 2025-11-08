#version 330

in vec2 fragCoord;
out vec4 fragColor;

// Input texture from first pass
uniform sampler2D uTexture;

// Screen resolution
uniform vec3 iResolution;
uniform float iTime;

// Post-processing effect parameters
uniform bool uInvertColors = false;
uniform bool uInvertRed = false;
uniform bool uInvertGreen = false;
uniform bool uInvertBlue = false;
uniform bool uInvertHue = false;
uniform bool uInvertSaturation = false;
uniform bool uInvertValue = false;
uniform bool uWavesX = false;
uniform bool uWavesY = false;

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

void main() {
    vec2 uv = fragCoord.xy / iResolution.xy;

    float waveAmplitude = 0.01;
    float waveFrequency = 100.0;
    float waveSpeed = 2.0;
    float waveX = sin(uv.y * waveFrequency + iTime * waveSpeed) * waveAmplitude;
    float waveY = cos(uv.x * waveFrequency * 0.7 + iTime * waveSpeed * 1.3) * waveAmplitude;
    
    if (uWavesX) {
        uv.x += waveX;
    }
    if (uWavesY) {
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
    
    fragColor = color;
}


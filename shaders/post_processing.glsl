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
uniform bool uWavesX = false;
uniform bool uWavesY = false;

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
    
    // Color inversion effect
    if (uInvertColors) {
        color.rgb = 1.0 - color.rgb;
    }
    
    fragColor = color;
}


#version 330

in vec2 fragCoord;
out vec4 fragColor;

// Input texture from first pass
uniform sampler2D uTexture;

// Screen resolution
uniform vec3 iResolution;

// Post-processing effect parameters
uniform bool uInvertColors = false;

void main() {
    vec2 uv = fragCoord.xy / iResolution.xy;
    vec4 color = texture(uTexture, uv);
    
    // Color inversion effect
    if (uInvertColors) {
        color.rgb = 1.0 - color.rgb;
    }
    
    fragColor = color;
}


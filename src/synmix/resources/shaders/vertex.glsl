#version 330

in vec2 in_texcoord_0;
out vec2 fragCoord;

uniform vec3 iResolution;

void main() {
    fragCoord = in_texcoord_0 * iResolution.xy;
    gl_Position = vec4((in_texcoord_0 * 2.0 - 1.0), 0.0, 1.0);
}

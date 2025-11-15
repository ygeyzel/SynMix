#version 330
in vec2 fragCoord;
out vec4 fragColor;

uniform vec3 iResolution;
uniform float iTime;

vec3 palette(float t) {
        vec3 a = vec3(0.388, 0.508, 0.500);
        vec3 b = vec3(-0.392, 0.488, 0.428);
        vec3 c = vec3(1.000, 1.000, 1.000);
        vec3 d = vec3(1.000, 1.328, 1.268);

        return a + b * cos(6.28318 * (c * t * d));
}

void main()
{
        vec2 uv = (fragCoord * 2.0 - iResolution.xy) / iResolution.y;
        vec2 uv0 = uv;
        vec3 finalColor = vec3(0.0);

        for (float i = 0.0; i < 7.0; i += 1.0) {
                uv = fract(uv * (0.5 + i / 3.0)) - 0.5;

                float d = length(uv) * exp(-length(uv0));

                vec3 col = palette(length(uv0) + (iTime / 15.0 * i));

                d = sin(d * 8. + sin(iTime / (1.0 + i)) + iTime) / 8.;
                d = abs(d);
                d = pow(0.01 / d, 1.5);

                col *= d;

                finalColor += col;
        }

        fragColor = vec4(finalColor, 1.0);
}

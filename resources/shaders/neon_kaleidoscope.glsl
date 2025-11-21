#version 330
in vec2 fragCoord;
out vec4 fragColor;

uniform vec3 iResolution;
uniform float iTime;

uniform float phase_r;
uniform float phase_g;
uniform float phase_b;

uniform float iMax; 

uniform float w_d; 
uniform float time_dilation;
uniform float uv_factor;
uniform float uvi_factor;


vec3 palette(float t) {
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(phase_r,phase_g,phase_b);

    return a + b*cos( 6.28318*(c*t+d) );
}

void main()
{
        vec2 uv = (fragCoord * 2.0 - iResolution.xy) / iResolution.y;
        vec2 uv0 = uv;
        vec3 finalColor = vec3(0.0);
        for (float i = 0.0; i < iMax; i += 1.0) {
                float time_tag = iTime*(1 + time_dilation * i / 15.0);
                uv = fract(uv * (uv_factor + uvi_factor*i/iMax)) - 0.5;

                float d = length(uv) * exp(-length(uv0));
                d = sin(d * w_d + time_tag) / 8.;
                d = abs(d);
                d = pow(0.01 / d, 1.5)/iMax*4.;

                vec3 col = palette(length(uv0) + time_tag);

                finalColor += col * d;
        }

        fragColor = vec4(finalColor, 1.0);
}

#version 330

out vec4 fragColor;
in vec2 fragCoord;

uniform vec3 iResolution;
uniform float iTime;

uniform float xOffset;
uniform float yOffset;

uniform float hueShift;
uniform float hueRange;
uniform float saturation;
uniform float brightness; //v
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

vec3 palette(float d) {
        return mix(vec3(0.2, 0.7, 0.9), vec3(1., 0., 1.), d);
}

vec2 rotate(vec2 p, float a) {
        float c = cos(a);
        float s = sin(a);
        return p * mat2(c, s, -s, c);
}

float map(vec3 p) {
        for (int i = 0; i < 8; ++i) {
                float t = iTime * 0.2;
                p.xz = rotate(p.xz, t);
                p.xy = rotate(p.xy, t * 1.89);
                p.xz = abs(p.xz);
                p.xz -= .5;
        }
        return dot(sign(p), p) / 5.;
}

vec4 rm(vec3 ro, vec3 rd) {
        float t = 0.;
        vec3 col = vec3(0.);
        float d;
        for (float i = 0.; i < 64.; i++) {
                vec3 p = ro + rd * t;
                d = map(p) * .5;
                if (d < 0.02) {
                        break;
                }
                if (d > 100.) {
                        break;
                }
                //col += vec3(0.6, 0.8, 0.8) / (400. * (d));
                col += (palette(length(p) * .1) + brightness * vec3(0.6, 0.8, 0.8)) / (400. * (d));
                t += d;
        }
        return vec4(col, 1. / (d * 100.));
}
void main()
{
        vec2 uv = (fragCoord - (iResolution.xy / 2.)) / iResolution.x;
        vec3 ro = vec3(0., 0., -50.);
        ro.xz = rotate(ro.xz, iTime);
        vec3 cf = normalize(-ro);
        vec3 cs = normalize(cross(cf, vec3(0., 1., 0.)));
        vec3 cu = normalize(cross(cf, cs));

        vec3 uuv = ro + cf * 3. + uv.x * cs + uv.y * cu;

        vec3 rd = normalize(uuv - ro);

        vec4 col = rm(ro, rd);

        fragColor = col;
}

/** SHADERDATA
{
  "url" : "https://www.shadertoy.com/view/tsXBzS"
  "title": "fractal pyramid",
  "description": "",
  "model": "car"
}
*/

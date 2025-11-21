#version 330


in vec2 fragCoord;
out vec4 fragColor;

uniform vec3 iResolution;
uniform float time; 

uniform bool CHAR_A;
uniform bool CHAR_C;
uniform bool CHAR_L;
uniform bool CHAR_X;

uniform float rController;

uniform float floatFragmentColor;
int fragmentColor = int(floatFragmentColor);

uniform float lineWidth;
uniform float lightness;
uniform float colerShade;
uniform float scale;
uniform float floatBrightness;
int brightness = int(floatBrightness);
uniform float frecImage;


vec2 mouse = vec2(0,0);


vec3 hsv2rgb(in vec3 c) {
  vec3 rgb = clamp( abs(mod(c.x * 6.0 + vec3(0.0,4.0,2.0),6.0)-3.0)-1.0, 0.0, 1.0 );
  rgb = rgb * rgb * (3.0-2.0 * rgb); // cubic smoothing   
  return c.z * mix( vec3(1.0), rgb, c.y);
}



float kfact = 1.0;

vec3 draw(float d, vec3 col, vec3 ccol, float pwidth) {
  col = mix(ccol,col,mix(1.0,smoothstep(-pwidth,pwidth,d-lineWidth),kfact));
  return col;
}

vec3 drawcircle(vec2 z, vec3 col, vec3 ccol, vec3 circle) {
  float d = abs(length(z-circle.xy) - sqrt(abs(circle.z)));
  return draw(d,col,ccol,fwidth(z.x));
}

vec3 drawline(vec2 z, vec3 col, vec3 ccol, vec2 line) {
  float d = abs(dot(z,line));
  return draw(d,col,ccol,fwidth(z.x));
}

vec2 invert(vec2 z, vec3 c) {
  z -= c.xy;
  float k = abs(c.z)/dot(z,z);
  z *= k;
  z += c.xy;
  return z;
}

bool inside(vec2 z, vec3 c) {
  z -= c.xy;
  if (c.z < 0.0) return dot(z,z) > abs(c.z);
  return dot(z,z) < abs(c.z);
}


////////////////////////////////////////////////////////////////////////////////
//
// Inversive Kaleidoscope II
// mla, 2020
//
// <mouse>: move free inversion circle
// a: just animation
// c: show circles
// l: show lines
// x: lock x coordinate for free circle
//
////////////////////////////////////////////////////////////////////////////////

const int NCIRCLES = 4;
const float AA = 2.0;
float R = rController;

vec3 circles[NCIRCLES] =
  vec3[](vec3(0,0,frecImage),
         vec3(-2,1,R),
         vec3(2,1,R),
         vec3(0,0,-5));
         
vec3 getcolor(vec2 z0, vec2 w) {
  vec2 z = z0;
  int i, N = fragmentColor;
  bool found = true;
  for (i = 0; i < N && found; i++) {
    for (int j = 0; j < NCIRCLES; j++) {
      found = false;
      vec3 c = circles[j];
      if (inside(z,c)) {
        z = invert(z,c);
        found = true;
        break;
      }
    }
  }
  vec3 col = vec3(0);
  if (i < N) col = hsv2rgb(vec3(float(i)/10.0,1,1));
  if (!CHAR_L) {
    vec3 ccol = vec3(0);
    for(int i = 0; i < NCIRCLES; i++) {
      col = drawcircle(z,col,ccol,circles[i]);
    }
  }
  if (!CHAR_C) {
    vec3 ccol = vec3(1);
    for(int i = 0; i < NCIRCLES; i++) {
      col = drawcircle(z0,col,ccol,circles[i]);
    }
  }
  return col;
}

void main() {
  vec3 color = vec3(brightness);
  vec2 w = vec2(0,-0.25) + vec2(0,cos(0.618*time));
  if (mouse.x > 0.0 && (!CHAR_A)) {
    w = (2.0*mouse.xy-iResolution.xy)/iResolution.y;
    w *= scale;
    if (CHAR_X) w.x = 0.0;
  }
  circles[0].xy = w;
  circles[1].x += sin(0.5*time);
  circles[2].x -= sin(0.5*time);
  for (float i = lightness; i < AA; i++) {
    for (float j = 0.0; j < AA; j++) {
      vec2 z = (2.0*(fragCoord+vec2(i,j)/AA)-iResolution.xy)/iResolution.y;
      z *= scale;
      z.y += 1.0; w.y += 1.0;
      color += getcolor(z,w);
    }
  }
  color /= AA*AA;
  color = pow(color,vec3(colerShade));
  fragColor = vec4(color,1.0);
}
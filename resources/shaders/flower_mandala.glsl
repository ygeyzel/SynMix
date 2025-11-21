#version 330

in vec2 fragCoord;
out vec4 fragColor;

uniform vec3 iResolution;
uniform float iTime;
uniform float time;

uniform bool CHAR_C;
uniform float lineBrightnes;
uniform bool CHAR_L;
uniform bool CHAR_M;


uniform float lightness;
uniform float scale;
uniform int fraction;
uniform float floatColorFraction;
int colorFraction = int(floatColorFraction);

uniform float floatColorControler;
int colorControler = int(floatColorControler);

uniform float anotherColorControler;

uniform float floatLeafNumber;
int leafNumber = int(floatLeafNumber);

uniform float lineWidth;

uniform float mouse_x;
uniform float mouse_y;
vec2 iMouse = vec2 (mouse_x, mouse_y);

uniform bool zoomMovment;
uniform float floatZoomSpeed;
int zoomSpeed = int(floatZoomSpeed);


////////////////////////////////////////////////////////////////////////////////
// Inversive Kaleidoscope
// mla, 2020
//
// <mouse>: move free inversion circle
// c: show circles
// l: show lines
// m: mouse
////////////////////////////////////////////////////////////////////////////////


const float PI = 3.1415927;

int timeMunipulation(int speed, int segment){
  return int(iTime * speed) % segment;
}

vec3 hsv2rgb(in vec3 c) {
  vec3 rgb = clamp( abs(mod(c.x*6.0+vec3(0.0,4.0,2.0),6.0)-3.0)-1.0, 0.0, 1.0 );
  rgb = rgb*rgb*(3.0-2.0*rgb); // cubic smoothing 
  return c.z * mix( vec3(1.0), rgb, c.y);
}


vec2 invert(vec2 z, vec3 c) {
  z -= c.xy;
  float k = c.z/dot(z,z);
  z *= k;
  z += c.xy;
  return z;
}

bool inside(vec2 z, vec3 c) {
  z -= c.xy;
  return dot(z,z) < abs(c.z);
}

float kfact = 0.8;
float lwidth = lineWidth;

vec3 draw(float d, vec3 col, vec3 ccol, float pwidth) {
  pwidth *= 0.1; //0.25;
  col = mix(ccol,col,mix(1.0,smoothstep(0.5*lwidth,max(pwidth,lwidth),d),kfact));
  //col = mix(ccol,col,mix(1.0,smoothstep(-pwidth,pwidth,d-lwidth),kfact));
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





int P = fraction;
vec3 getcolor(vec2 z0, vec2 w) {
  z0 += 1e-2;
  vec2 z = z0;
  float r2 = 2.0-cos(time);
  float theta = PI/float(P);
  vec2 l0 = vec2(0,1);
  vec2 l1 = vec2(sin(theta),-cos(theta));
  vec3 c0 = vec3(0,0,r2);
  vec3 c1 = vec3(w,1.0);
  int i, N = colorFraction;
  for (i = colorControler; i < N; i++) {
    for (int j = leafNumber; j < P; j++) {
      if (dot(z,l0) < 0.0) z = reflect(z,l0);
      else if (dot(z,l1) < 0.0) z = reflect(z,l1);
      else break;
    }
    if (inside(z,c1)) z = invert(z,c1);
    else if (inside(z,c0)) z = invert(z,c0);
    else break;
  }
  if (i == N) return vec3(0);
  vec3 col;
  col = hsv2rgb(vec3(float(i)/anotherColorControler,1,1));
  if (CHAR_L) {
    vec3 ccol = vec3(lineBrightnes);
    col = drawline(z,col,ccol,l0);
    col = drawline(z,col,ccol,l1);
    col = drawcircle(z,col,ccol,c0);
    col = drawcircle(z,col,ccol,c1);
  }
  if (CHAR_C) {
    vec3 ccol = vec3(0);
    col = drawline(z0,col,ccol,l0);
    col = drawline(z0,col,ccol,l1);
    col = drawcircle(z0,col,ccol,c0);
    col = drawcircle(z0,col,ccol,c1);
  }
  return col;
}

void main() {
  float AA = 2.0;
  vec3 color = vec3(lightness);
  for (float i = 0.0; i < AA; i++) {
    for (float j = 0.0; j < AA; j++) {
      float zoom;
      if (zoomMovment) zoom = timeMunipulation(zoomSpeed, 20);
      
      else zoom = 2.0;

      vec2 z = scale*(zoom*(fragCoord+vec2(i,j)/AA)-iResolution.xy)/iResolution.y;

      
      vec2 w = vec2(2.0,0.25)+vec2(-0.25*sin(0.618*time),0.5*cos(0.618*time));
      if (iMouse.x > 0.0 && (!CHAR_M)) w = scale*(2.0*iMouse.xy-iResolution.xy)/iResolution.y;
      color += getcolor(z,w);
    }
  }
  color /= AA*AA;
  color = pow(color,vec3(0.4545));
  fragColor = vec4(color,1.0);
}


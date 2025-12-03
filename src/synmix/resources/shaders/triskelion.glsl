#version 330

// from: https://www.shadertoy.com/view/dl3SRr

in vec2 fragCoord;
out vec4 fragColor;

uniform vec3 iResolution;
uniform float iTime;

// parameters
uniform float mx; // (0.5 to 1.5) 1.0
uniform float my; // (0.5 to 1.5) 1.0
uniform float mw; // (0.5 to 1.5) 1.0
uniform float tx; // (0.5 to 1.5) 1.0
uniform float ty; // (0.5 to 1.5) 1.0
uniform float dp; // (0.75 to 1.25) 1.0
uniform float iMax; // (10 to 30) 24.0
uniform float t3_factor; // (0.0 to 5.0) 0.0
uniform float d_factor; // (0.5 to 3.0) 1.0
uniform float p_factor; // (10.0 to 20.0) 5.0
uniform float t_factor; // (0.9 to 1.1) 1.0


// Neon circles blooming into a fractal hexagonal grid.
// Inspiration:
// - https://www.shadertoy.com/view/mly3Dd - Glowing concentric circles + square
// grid folding
// - https://www.shadertoy.com/view/NtBSRV - Hexagonal cells

// Biased rainbow color map. Will be squared later.
vec3 pal(float a) { 
  return 0.5 + cos(3.0 * a + vec3(2, 1, 0)); 
}

// Shift and fold into a vertex-centered grid.
vec2 fold(vec2 p) {
  vec4 m = vec4(2*mx, -1*my, 0, sqrt(3.)*mw);
  // center at vertex
  p.y += m.w / 3.0;
  // triangular coordinates (x →, y ↖, x+y ↗)
  vec2 t = mat2(m) * p;
  // fold into hexagonal cells
  return p - 0.5 * mat2(m.xzyw) * round((floor(t) + ceil(t.x*tx + t.y*ty)) / 3.0);
}

void main() {
  // dissonant timers
  float t = iTime / 4.0, t2 = t * 0.618034, t3 = t * 1.4142135;
  // rotation and scale: 0.9 [smooth] .. 1.1 [fractal]
  mat2 M = mat2(cos(t), sin(t), -sin(t), cos(t)) * (1.05 - 0.1 * cos(t2));

  // y: -1 .. 1
  vec2 p = (2.0 * fragCoord - iResolution.xy) / iResolution.y;
  // animation phase is based on distance to center
  float d = 0.5 * length(p);
  d = pow(d, dp);

  vec3 sum = vec3(0);
  for (float i = 0.0; i < iMax; i++) {
    float t3_tag = t3 + i/iMax*t3_factor;
    // rotate and scale, fold
    p = fold(M * p); 
    // interfering concentric circles
    sum += pal(0.01 * i - d + t2) / cos(d * d_factor - t3_tag * t_factor + length(p) * p_factor);
  }
  sum = sum / iMax * 24.0;

  // square the sum for better contrast
  fragColor = vec4(0.0002 * sum * sum, 1);
}

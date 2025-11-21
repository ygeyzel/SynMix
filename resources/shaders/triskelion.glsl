#version 330

// from: https://www.shadertoy.com/view/dl3SRr

in vec2 fragCoord;
out vec4 fragColor;

uniform vec3 iResolution;
uniform float iTime;

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
  vec4 m = vec4(2, -1, 0, sqrt(3.));
  // center at vertex
  p.y += m.w / 3.0;
  // triangular coordinates (x →, y ↖, x+y ↗)
  vec2 t = mat2(m) * p;
  // fold into hexagonal cells
  return p - 0.5 * mat2(m.xzyw) * round((floor(t) + ceil(t.x + t.y)) / 3.0);
}

void main() {
  // dissonant timers
  float t = iTime / 4.0, t2 = t * 0.618034, t3 = t * 1.4142135;
  // rotation and scale: 0.9 [smooth] .. 1.1 [fractal]
  mat2 M = mat2(cos(t), sin(t), -sin(t), cos(t)) * (1.0 - 0.1 * cos(t2));

  // y: -1 .. 1
  vec2 p = (2.0 * fragCoord - iResolution.xy) / iResolution.y;
  // animation phase is based on distance to center
  float d = 0.5 * length(p);

  vec3 sum = vec3(0);
  for (float i = 0.0; i < 24.0; i++) {
    // rotate and scale, fold
    p = fold(M * p); 
    // interfering concentric circles
    sum += pal(0.01 * i - d + t2) / cos(d - t3 + 5.0 * length(p));
    // Use pal(...)/abs(cos(...)) for additive circles. I like the interference
    // effect without the abs.
  }

  // square the sum for better contrast
  fragColor = vec4(0.0002 * sum * sum, 1);
}

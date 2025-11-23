#version 330
// based on https://www.shadertoy.com/view/MtjSRw

in vec2 fragCoord;
out vec4 fragColor;
uniform vec3 iResolution;

// params
uniform float x;
uniform float y;
uniform float n;

uniform float zoom_m;
uniform float zoom_j;

uniform float x_j;
uniform float y_j;

const int MAX_ITERATIONS = 128;

// cosine based palette, 4 vec3 params
vec3 palette( in float t, in vec3 a, in vec3 b, in vec3 c, in vec3 d )
{
    return a + b*cos( 6.283185*(c*t+d) );
}

struct complex {
  float real;
  float imaginary;
};

float fractal(complex c, complex z, float n) {
  for (int iteration = 0; iteration < MAX_ITERATIONS; iteration++) {
    // z <- z^n + c
    float s = pow(z.real * z.real + z.imaginary * z.imaginary, n / 2.);
    float a = float(n) * atan(z.imaginary, z.real);

    z.real = s * cos(a) + c.real;
    z.imaginary = s * sin(a) + c.imaginary;

    float abs_z_2 = z.real * z.real + z.imaginary * z.imaginary;
    if (abs_z_2 > 4.0) {
      float c = float(iteration + 1) - log(log(abs_z_2)) / log(n);
      return c / float(MAX_ITERATIONS);
    }
  }

  return 0.0;
}

float mandelbrot(vec2 coordinate, float n) {
  complex c = complex(coordinate.x, coordinate.y);
  complex z = complex(0.0, 0.0);

  return fractal(c, z, n);
}

float julia(vec2 coordinate, vec2 offset, float n) {
  complex c = complex(offset.x, offset.y);
  complex z = complex(coordinate.x, coordinate.y);

  return fractal(c, z, n);
}

vec2 fragCoordToXY(vec2 fragCoord) {
  vec2 relativePosition = fragCoord.xy / iResolution.xy;
  float aspectRatio = iResolution.x / iResolution.y;

  vec2 cartesianPosition = (relativePosition - 0.5) * 2.0 * 2.0;
  cartesianPosition.x *= aspectRatio;

  return cartesianPosition;
}

vec3 juliaColor(float v) {
  return palette(v, vec3(0.4, 0.8, 0.5), vec3(0.2, 0.2, 0.4), vec3(1.0, 2.0, 1.0), vec3(0.25, 0.00, 0.25)) * pow(v, 0.75);
}

vec3 mandelbrotColor(float v) {
  return palette(v, vec3(0.8, 0.5, 0.4), vec3(0.2, 0.4, 0.2), vec3(2.0, 1.0, 1.0), vec3(0.00, 0.25, 0.25)) * pow(v, 0.75);
}

vec3 clickPointColor(float v) {
  return vec3(0.0, 0.0, 1.0*v);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 coordinate = fragCoordToXY(fragCoord);
  vec2 clickPosition = vec2(x, y);

  vec2 j0 = vec2(-0.33, 0.0);
  vec2 j0t = j0;
  vec2 j1 = vec2(-0.77, 0.98);
  vec2 j1t = vec2(-0.51, 0.59);
  vec2 j_zoom_center = (clickPosition-j0) / (j1-j0)*(j1t-j0t)+j0t;

  float juliaValue = julia(
    coordinate * pow(2.0, -zoom_j)
    + (vec2(x_j, y_j) - j_zoom_center) * pow(2.0, -zoom_j) + j_zoom_center, 
    clickPosition, n
  );

  vec2 coordinate2 = coordinate - clickPosition;
  coordinate2 = coordinate2 * pow(2.0, -zoom_m);
  coordinate2 = coordinate2 + clickPosition;
  float mandelbrotValue = mandelbrot(coordinate2, n);

  float clickPoint =
      smoothstep(0.02 * 1.1, 0.02, length(clickPosition - coordinate));

  fragColor = vec4(
    clamp(mandelbrotColor(mandelbrotValue), 0.0, 1.0)
    + clamp(juliaColor(juliaValue), 0.0, 1.0)
    + clamp(clickPointColor(clickPoint), 0.0, 1.0)
    , 1.0);
}

void main() {
  mainImage(fragColor, fragCoord);
}

#version 330 core

in vec2 fragCoord;
out vec4 fragColor;

uniform vec3 iResolution;
uniform float iTime;
uniform float u_offsetX;
uniform float u_offsetY;
uniform float u_zoom; // 0 to 8, used as exponent: zoom = 10^u_zoom
uniform float u_rotation; // Normalized 0.0 to 1.0, mapped to 0 to 2π radians

const int MAX_ITER = 256;

// Color palette function - creates smooth, vibrant colors
vec3 palette(float t) {
        vec3 a = vec3(0.5, 0.5, 0.5);
        vec3 b = vec3(0.5, 0.5, 0.5);
        vec3 c = vec3(1.0, 1.0, 1.0);
        vec3 d = vec3(0.263, 0.416, 0.557);

        return a + b * cos(6.28318 * (c * t + d));
}

// Apply 2D rotation to a point
vec2 rotate2D(vec2 point, float angle) {
        float cosR = cos(angle);
        float sinR = sin(angle);
        return vec2(
                point.x * cosR - point.y * sinR,
                point.x * sinR + point.y * cosR
        );
}

// Convert screen coordinates to normalized UV coordinates
vec2 screenToUV(vec2 fragCoord, vec3 resolution) {
        return (fragCoord.xy - 0.5 * resolution.xy) / resolution.y;
}

// Apply transformations to get complex plane coordinate
vec2 uvToComplex(vec2 uv, float zoom, float rotationNormalized, vec2 offset) {
        float frameHeight = 3.0 / zoom;

        // Scale offset by zoom (at high zoom, offset moves smaller distances in complex plane)
        vec2 scaledOffset = offset / zoom;

        // Apply offset in screen space
        vec2 uvWithOffset = uv + scaledOffset;

        // Rotate around the center
        float angle = rotationNormalized * 6.28318;
        vec2 rotatedUV = rotate2D(uvWithOffset, angle);

        // Scale to complex plane
        return rotatedUV * frameHeight;
}

// Mandelbrot iteration - returns number of iterations and final z value
struct IterationResult {
        int iterations;
        vec2 z;
        float minDist;
        float avgDist;
};

IterationResult mandelbrotIterate(vec2 c) {
        IterationResult result;
        result.z = vec2(0.0);
        result.minDist = 1e10;
        result.avgDist = 0.0;

        for (result.iterations = 0; result.iterations < MAX_ITER; result.iterations++) {
                // z = z^2 + c
                result.z = vec2(
                                result.z.x * result.z.x - result.z.y * result.z.y,
                                2.0 * result.z.x * result.z.y
                        ) + c;

                // Track orbit behavior
                float dist = dot(result.z, result.z);
                result.minDist = min(result.minDist, dist);
                result.avgDist += dist;

                // Check if escaped
                if (dist > 4.0) break;
        }

        result.avgDist /= float(MAX_ITER);
        return result;
}

// Color the interior of the set
vec3 colorInterior(IterationResult result) {
        float interiorT = sqrt(result.minDist) * 0.5 + sqrt(result.avgDist) * 0.3;
        return palette(interiorT + 0.5) * 0.4;
}

// Color the exterior of the set with smooth coloring
vec3 colorExterior(IterationResult result) {
        float smoothIter = float(result.iterations) - log2(log2(dot(result.z, result.z))) + 4.0;
        float t = smoothIter / float(MAX_ITER);
        return palette(t);
}

void main() {
        // Calculate actual zoom level (exponential)
        float zoom = pow(10.0, u_zoom);

        // Calculate zoom and transformations
        vec2 uv = screenToUV(fragCoord, iResolution);
        vec2 offset = vec2(u_offsetX, u_offsetY);
        vec2 c = uvToComplex(uv, zoom, u_rotation, offset);

        // Perform Mandelbrot iteration
        IterationResult result = mandelbrotIterate(c);

        // Choose color based on whether point is inside or outside the set
        vec3 color;
        if (result.iterations == MAX_ITER) {
                color = colorInterior(result);
        } else {
                color = colorExterior(result);
        }

        fragColor = vec4(color, 1.0);
}

#version 330


in vec2 fragCoord;
out vec4 fragColor;

uniform vec3 iResolution;
uniform float iTime;

uniform float red;
uniform float green;
uniform float blue;

// uniform int colorFraction;

// vec3 get_color()
// {
//     vec3 color = (red / 255.0, green / 255.0, blue / 255.0);
//     return color;
// }

// float getRed(vec2 uv)
// {
//     return (uv.x + uv.y) * sin(red);
// }

// float getGreen(vec2 uv)
// {
//     return (uv.y + uv.x) * tan(green);
// }

// float getBlue(vec2 uv)
// {
//     return (uv.x + uv.y) * cos(blue);
// }

// vec2 fraction_surfece(vec2 uv0)
// {
//     vec2 uv = cos(colorFraction * uv0);
//     return uv;
// }   

// vec3 getShapeColor(vec2 uv0)
// {
//     vec2 uv = fraction_surfece(uv0);
//     vec3 color = vec3 (getRed(uv), getGreen(uv), getBlue(uv));
//     return color ;
// }

// vec4 circle(vec2 uv, vec2 pos, float rad, vec3 color) 
// {
//     float d = length(pos - uv) - rad;
//     float t = clamp(d, 0.0, 1.0);
//     return vec4 (color, 1.0 - t);
// }

// vec4 backruond(vec3 color)
// {
//     return vec4 (color, 1.0);
// }   

// void main()
// {
//     vec2 uv0 = fragCoord/iResolution.xy;  
//     vec3 color = getShapeColor(uv0); 
//     vec4 layer_1 = circle(uv0, vec2 (1,1), 10, color);    
//     // fragColor = layer_1;
//     color = 0 * color;
//     vec4 layer_2 = backruond(color);    
//     fragColor = mix(layer_1, layer_2, 0);
// }





/**
 * @author jonobr1 / http://jonobr1.com/
 */

/**
 * Convert r, g, b to normalized vec3
 */
vec3 rgb(float r, float g, float b) {
    return vec3(r / 255.0, g / 255.0, b / 255.0);
}

/**
 * Draw a circle at vec2 `pos` with radius `rad` and
 * color `color`.
 */
vec4 circle(vec2 uv, vec2 pos, float rad, vec3 color) {
    float d = length(pos - uv) - rad;
    float t = clamp(d, 0.0, 1.0);
    return vec4(color, 1.0 - t);
}

void main() 
{

    vec2 uv = fragCoord.xy;
    vec2 center = iResolution.xy * 0.5;
    float radius = 0.25 * iResolution.y;

    // Background layer
    vec4 layer1 = vec4(rgb(210.0, 222.0, 228.0), 1.0);
    
    // Circle
    vec3 red = rgb(225.0, 95.0, 60.0);
    vec4 layer2 = circle(uv, center, radius, red);
    
    // Blend the two
    fragColor = mix(layer1, layer2, layer2.a);

}
#version 330

in vec2 fragCoord;
out vec4 fragColor;

uniform vec3 iResolution;
uniform float iTime;
uniform int iFrame;
uniform vec3 iMouse;



// Controllable parameters



// Wonderland

// Base:
//         Green Field Diorama by Gallo
//         https://www.shadertoy.com/view/7dSGW1
// Portal mechanics:
//         TARDIS by efelo
//         https://www.shadertoy.com/view/7dKSRG
// Glow effect:
//         3D GLOW TUTORIAL by alro
//         https://www.shadertoy.com/view/7stGWj

// SDF, Maths and CG techniques:
//         IQ's articles and shaders:
//         https://iquilezles.org/articles/
//         Raymarching - Primitives: https://www.shadertoy.com/view/Xds3zN
//         Rainforest by IQ: https://www.shadertoy.com/view/4ttSWf
//         Box Mapping: https://www.shadertoy.com/view/MtsGWH
//         Box Function: https://iquilezles.org/articles/boxfunctions
//         Extrusion and Revolution SDF: https://www.shadertoy.com/view/4lyfzw
//         Elongation SDF: https://www.shadertoy.com/view/Ml3fWj
//         Many more..!!: https://www.shadertoy.com/user/iq

// Utility functions:
//         Hash without Sine by Dave_Hoskins: 
//         https://www.shadertoy.com/view/4djSRW
//
//         Shortest rotation dot! by FabriceNeyret2
//         https://www.shadertoy.com/view/XlsyWX
//
//         hg_sdf:
//         https://mercury.sexy/hg_sdf/

// Inspiration and endless knowledge:
//         Shadertoy Community – thank you for everything you share

// Created with help from AI:
// Grok (≈90%), Claude (≈8%), Gemini (≈2%)
// Free tiers - We really are heading into an age of creative abundance!


// Any suggestions to improve performance, code, art — anything at all — are MOST welcome!
// Currently ~20 fps without AA, ~2.5 fps with AA=2 @ 1080x607 on my machine.
// Performance & compile time definitely needs improvement.
// Animations in next version, hopefully! 

//---------------------------------------------------------------------------

// Controllable parameters
// change this one number to resize figers

uniform float ALICE_SIZE;
uniform float ALICE_SPIN_ANGEL;
uniform float BUNNY_SIZE;
uniform float HAPPY_FLOWER_SIZE;
uniform float MUSHROOM1_SIZE;
uniform float MUSHROOM2_SIZE;
uniform float MUSHROOM1_SPOT_DENSITY;
uniform float MUSHROOM2_SPOT_DENSITY;
uniform int IS_MUSHROOM1_SPOT_SIZE_MOD;
uniform int IS_MUSHROOM2_SPOT_SIZE_MOD;
uniform float FLOWER_BED_SIZE; // 1.0 = original size
uniform float BIFROST_LOOPS;
uniform float TREE_SIZE;   // 1.0 = original size
uniform float CLOUD_ROTATION_ANGLE;   // radians; static angle or drive with iTime for continuous spin
uniform float BUNNY_EAR_TAIL_BALANCE;   // 1.0 = default; <1 = smaller ears/bigger tail; >1 = bigger ears/smaller tail
uniform int FLOWER_PETAL_ROTATION_MOD;
uniform bool IS_BUNNY_WAVE;



#define BUNNY_WAVE_ANGLE (IS_BUNNY_WAVE ? sin(iTime * 4) : 0)   // radians; drive with sin(iTime*speed) for waving motion, or a static angle
#define BUNNY_WAVE_RANGE_SCALE 0.1   // dampens the incoming angle; 1.0 = full range, lower = narrower swing


#define FLOWER_PETAL_ROTATION iTime * FLOWER_PETAL_ROTATION_MOD   // radians; static angle, or drive with iTime for continuous spin

#define  BIFROST_BOW_HEIGHT 0.0   // DO NOT TUCH.

#define BIFROST_SWAY_AMOUNT 0.5

#define BIFROST_LOCAL_HALF_LEN 0.9                  // matches sdBifrost's box z half-length (1.8*0.5)
#define BIFROST_Z_START (-BIFROST_LOCAL_HALF_LEN)    // local-frame box edge (start)
#define BIFROST_Z_END    (BIFROST_LOCAL_HALF_LEN)    // local-frame box edge (castle end)

#define BIFROST_WARP_FREQ  (PI / (BIFROST_Z_END - BIFROST_Z_START))
#define BIFROST_MAX_SLOPE  (BIFROST_SWAY_AMOUNT * BIFROST_WARP_FREQ * (1.0 + BIFROST_LOOPS))
#define BIFROST_LIPSCHITZ  sqrt(1.0 + BIFROST_MAX_SLOPE*BIFROST_MAX_SLOPE)


#define BIFROST_GATE_X_CORRECTION 0.495   // cancels the fixed lateral offset from worldToBifrost's origin subtraction

#define BIFROST_START_Y 0.0
#define BIFROST_END_Y 0.5529999999999999

#define BIFROST_CULL_HALF_X (BIFROST_GATE_X_CORRECTION + BIFROST_SWAY_AMOUNT + 0.3)
#define BIFROST_CULL_HALF_Y (BIFROST_END_Y + 0.3)
#define BIFROST_CULL_HALF_Z (BIFROST_LOCAL_HALF_LEN + 0.2)

#define BIFROST_CULL_CENTER vec3(0.5, 0.2, .69)
#define BIFROST_CULL_SIZE   vec3(BIFROST_CULL_HALF_X, BIFROST_CULL_HALF_Y, BIFROST_CULL_HALF_Z)




// #define IS_MUSHROOM1_SPOT_SIZE_MOD true
#define MUSHROOM1_SPOT_SIZE_MOD (IS_MUSHROOM1_SPOT_SIZE_MOD != 1 ? 2.0 : 1.0)

// #define IS_MUSHROOM2_SPOT_SIZE_MOD true
#define MUSHROOM2_SPOT_SIZE_MOD (IS_MUSHROOM2_SPOT_SIZE_MOD != 1 ? 2.0 : 1.0)

// #define ALICE_SIZE 5.0  // original 0.9
// #define BUNNY_SIZE 2.5 // original 1.2

// --- derived from ALICE_SIZE, don't touch ---

#define ALICE_SCALE          ALICE_SIZE
#define ALICE_Y_OFFSET  (0.449 - 0.0667 * ALICE_SIZE)
#define ALICE_LOCAL_CENTER   (-0.265)
#define ALICE_LOCAL_BOUND    (0.305)
#define ALICE_WORLD_CENTER_Y ((-0.265 + ALICE_Y_OFFSET) / ALICE_SIZE)
#define ALICE_WORLD_BOUND    (0.35 / ALICE_SIZE)

// --- derived from BUNNY_SIZE, don't touch ---

#define BUNNY_SCALE BUNNY_SIZE
#define BUNNY_Y_OFFSET (0.075 - 0.0667 * BUNNY_SIZE)
#define BUNNY_Z_OFFSET  (0.766 * BUNNY_SIZE)//0.919 original
#define BUNNY_X_OFFSET  (-0.294 * BUNNY_SIZE)//-0.553 original
#define BUNNY_POS vec3(BUNNY_X_OFFSET, BUNNY_Y_OFFSET, BUNNY_Z_OFFSET)
#define BUNNY_LOCAL_CENTER   (-0.265)
#define BUNNY_LOCAL_BOUND (0.1)
#define BUNNY_WORLD_CENTER_Y ((-0.265 + BUNNY_Y_OFFSET) / BUNNY_SIZE)
#define BUNNY_WORLD_BOUND    (0.35 / BUNNY_SIZE)

// --- derived from BUNNY_EAR_TAIL_BALANCE ---
#define BUNNY_EAR_SCALE  BUNNY_EAR_TAIL_BALANCE
#define BUNNY_TAIL_SCALE (2.0 - BUNNY_EAR_TAIL_BALANCE)   // inverse relationship, pinned so BALANCE=1.0 gives both =1.0
#define BUNNY_EAR_EXTRA_REACH  (max(BUNNY_EAR_SCALE - 1.0, 0.0) * 0.4)   // extra ear reach beyond baseline, local space
#define BUNNY_TAIL_EXTRA_REACH (max(BUNNY_TAIL_SCALE - 1.0, 0.0) * 0.08) // extra tail reach beyond baseline, local space
#define BUNNY_HEAD_Y_MAX (1.0 + max(BUNNY_EAR_SCALE - 1.0, 0.0) * 0.36)

// #define MUSHROOM1_SPOT_DENSITY  0.1   // bigger = fewer spots, smaller = more spots
#define MUSHROOM1_SPOT_SIZE_MIN 0.01 * MUSHROOM1_SPOT_SIZE_MOD // minimum spot size
#define MUSHROOM1_SPOT_SIZE_MAX 0.025 * MUSHROOM1_SPOT_SIZE_MOD// maximum spot size

// #define MUSHROOM1_SIZE   0.5
#define MUSHROOM1_SCALE  (2.5 * MUSHROOM1_SIZE)
#define MUSHROOM1_POS_Y  -.06
#define MUSHROOM1_POS    vec3(-0.7, MUSHROOM1_POS_Y, -.8)




// #define MUSHROOM2_SPOT_DENSITY  0.07   // bigger = fewer spots, smaller = more spots
#define MUSHROOM2_SPOT_SIZE_MIN 0.01 * MUSHROOM2_SPOT_SIZE_MOD // minimum spot size
#define MUSHROOM2_SPOT_SIZE_MAX 0.025 * MUSHROOM2_SPOT_SIZE_MOD// maximum spot size

// #define MUSHROOM2_SIZE   1.0
#define MUSHROOM2_SCALE  (2.5 * MUSHROOM2_SIZE)
#define MUSHROOM2_POS_Y  -.06
#define MUSHROOM2_POS    vec3(0.7, MUSHROOM2_POS_Y, -.8)


// --- derived from HAPPY_FLOWER_SIZE, don't touch ---
#define TALKING_FLOWER_SCALE HAPPY_FLOWER_SIZE
// #define TALKING_FLOWER_Y_OFFSET (-0.065 - 0.0867 * (HAPPY_FLOWER_SIZE - 1.2)) // tweak the 0.0667 coefficient to taste
#define TALKING_FLOWER_Y_OFFSET (-0.065)   // constant ground height, no size term
#define TALKING_FLOWER_POS vec3(-1., TALKING_FLOWER_Y_OFFSET, -.3)



#if HW_PERFORMANCE==0
#define AA 1
#else
#define AA 2   // make this 2 or 3 for antialiasing
#endif

#define PI 3.14159265

//---------------------------------------------------------------
// NOISE FUNCTIONS
// Hash without Sine by Dave_Hoskins: https://www.shadertoy.com/view/4djSRW
//---------------------------------------------------------------
float hash11(float p) {
    p = fract(p * .1031);
    p *= p + 33.33;
    p *= p + p;
    return fract(p);
}

float hash12(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * .1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float hash13(vec3 p) {
    p = fract(p * vec3(0.1031, 0.11369, 0.13787));
    p += dot(p, p.yxz + 19.19);
    return fract((p.x + p.y + p.z) * p.x);
}

vec2 hash22( vec2 p ) 
{
    const vec2 k = vec2( 0.3183099, 0.3678794 );
    float n = 111.0*p.x + 113.0*p.y;
    return fract(n*fract(k*n));
}
//---------------------------------------------------------------

//---------------------------------------------------------------
// UTILITY FUNCTIONS
//---------------------------------------------------------------

// Shortest rotation dot by @FabriceNeyret2
// https://www.shadertoy.com/view/XlsyWX
#define rot2d(theta) mat2(cos(theta+vec4(0,33,11,0)))

//-----------------------------------------------
// https://iquilezles.org/articles/distfunctions
//-----------------------------------------------

float dot2( in vec2 v ) { return dot(v,v); }
float dot2( in vec3 v ) { return dot(v,v); }
float ndot( in vec2 a, in vec2 b ) { return a.x*b.x - a.y*b.y; }

float sdHexagon( in vec2 p, in float r )
{
    const vec3 k = vec3(-0.866025404,0.5,0.577350269);
    p = abs(p);
    p -= 2.0*min(dot(k.xy,p),0.0)*k.xy;
    p -= vec2(clamp(p.x, -k.z*r, k.z*r), r);
    return length(p)*sign(p.y);
}

float sdTunnel( in vec2 p, in vec2 wh )
{
    p.x = abs(p.x); p.y = -p.y;
    vec2 q = p - wh;

    float d1 = dot2(vec2(max(q.x,0.0),q.y));
    q.x = (p.y>0.0) ? q.x : length(p)-wh.x;
    float d2 = dot2(vec2(q.x,max(q.y,0.0)));
    float d = sqrt( min(d1,d2) );
    
    return (max(q.x,q.y)<0.0) ? -d : d;
}

float sdPie( in vec2 p, in vec2 c, in float r )
{
    p.x = abs(p.x);
    float l = length(p) - r;
    float m = length(p - c*clamp(dot(p,c),0.0,r) );
    return max(l,m*sign(c.y*p.x-c.x*p.y));
}

float sdSphere( vec3 p, float s )
{
    return length(p)-s;
}

float sdBox( vec3 p, vec3 b )
{
  vec3 q = abs(p) - b;
  return length(max(q,0.0)) + min(max(q.x,max(q.y,q.z)),0.0);
}

float sdRoundBox( vec3 p, vec3 b, float r )
{
  vec3 q = abs(p) - b + r;
  return length(max(q,0.0)) + min(max(q.x,max(q.y,q.z)),0.0) - r;
}

float sdCone( vec3 p, vec2 c, float h )
{
  // c is the sin/cos of the angle, h is height
  // Alternatively pass q instead of (c,h),
  // which is the point at the base in 2D
  vec2 q = h*vec2(c.x/c.y,-1.0);
    
  vec2 w = vec2( length(p.xz), p.y );
  vec2 a = w - q*clamp( dot(w,q)/dot(q,q), 0.0, 1.0 );
  vec2 b = w - q*vec2( clamp( w.x/q.x, 0.0, 1.0 ), 1.0 );
  float k = sign( q.y );
  float d = min(dot( a, a ),dot(b, b));
  float s = max( k*(w.x*q.y-w.y*q.x),k*(w.y-q.y)  );
  return sqrt(d)*sign(s);
}

float sdCone(vec3 p, vec3 a, vec3 b, float ra, float rb)
{
    float rba  = rb-ra;
    float baba = dot(b-a,b-a);
    float papa = dot(p-a,p-a);
    float paba = dot(p-a,b-a)/baba;
    float x = sqrt( papa - paba*paba*baba );
    float cax = max(0.0,x-((paba<0.5)?ra:rb));
    float cay = abs(paba-0.5)-0.5;
    float k = rba*rba + baba;
    float f = clamp( (rba*(x-ra)+paba*baba)/k, 0.0, 1.0 );
    float cbx = x-ra - f*rba;
    float cby = paba - f;
    float s = (cbx < 0.0 && cay < 0.0) ? -1.0 : 1.0;
    return s*sqrt( min(cax*cax + cay*cay*baba,
                       cbx*cbx + cby*cby*baba) );
}

float sdRoundCone(vec3 p, vec3 a, vec3 b, float r1, float r2)
{
    // sampling independent computations (only depend on shape)
    vec3  ba = b - a;
    float l2 = dot(ba,ba);
    float rr = r1 - r2;
    float a2 = l2 - rr*rr;
    float il2 = 1.0/l2;
    
    // sampling dependant computations
    vec3 pa = p - a;
    float y = dot(pa,ba);
    float z = y - l2;
    float x2 = dot2( pa*l2 - ba*y );
    float y2 = y*y*l2;
    float z2 = z*z*l2;

    // single square root!
    float k = sign(rr)*rr*rr*x2;
    if( sign(z)*a2*z2 > k ) return  sqrt(x2 + z2)        *il2 - r2;
    if( sign(y)*a2*y2 < k ) return  sqrt(x2 + y2)        *il2 - r1;
                            return (sqrt(x2*a2*il2)+y*rr)*il2 - r1;
}

float sdEllipsoid( in vec3 p, in vec3 r ) // approximated
{
    float k0 = length(p/r);
    float k1 = length(p/(r*r));
    return k0*(k0-1.0)/k1;
}

float sdTorus( vec3 p, vec2 t )
{
    return length( vec2(length(p.xz)-t.x,p.y) )-t.y;
}

float sdCylinder( vec3 p, vec3 c )
{
  return length(p.xz-c.xy)-c.z;
}

float sdCylinder( vec3 p, vec2 h )
{
    vec2 d = abs(vec2(length(p.xz),p.y)) - h;
    return min(max(d.x,d.y),0.0) + length(max(d,0.0));
}

float sdVerticalCapsule( vec3 p, float h, float r )
{
  p.y -= clamp( p.y, 0.0, h );
  return length( p ) - r;
}

float sdVesicaSegment( in vec3 p, in vec3 a, in vec3 b, in float w )
{
    // orient and project to 2D
    vec3  c = (a+b)*0.5;
    float h = length(b-a);
    vec3  v = (b-a)/h;
    float y = dot(p-c,v);
    vec2  q = vec2(length(p-c-y*v),abs(y));
    
    // shape constants
    h *= 0.5;
    w *= 0.5;
    float d = 0.5*(h*h-w*w)/w;
    
    // feature selection (vertex or body)
    vec3  t = (h*q.x < d*(q.y-h)) ? vec3(0.0,h,0.0) : vec3(-d,0.0,d+w);
 
    // distance
    return length(q-t.xy) - t.z;
}

float sdCapsule( vec3 p, vec3 a, vec3 b, float r )
{
  vec3 pa = p - a, ba = b - a;
  float h = clamp( dot(pa,ba)/dot(ba,ba), 0.0, 1.0 );
  return length( pa - ba*h ) - r;
}

float sdTriPrism( vec3 p, vec2 h )
{
  vec3 q = abs(p);
  return max(q.z-h.y,max(q.x*0.866025+p.y*0.5,-p.y)-h.x*0.5);
}

vec3 opRepetition(inout vec3 p, in vec3 s)
{
    vec3 cellId = floor(p / s);
    p -= (cellId + 0.5) * s;
    return cellId;
}

float opLimitedRepetition(inout float p, float spacing, int numLayers) {
    float cell = clamp(round(p / spacing), 0.0, float(numLayers - 1));
    p -= cell * spacing;
    return cell;
}

float smin(float a, float b, float k) {
    k *= 4.0;
    float h = max(k - abs(a - b), 0.0) / k;
    return min(a, b) - h * h * k * (1.0 / 4.0);
}

float smax(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0) / k;
    return max(a, b) + h * h * k * (1.0 / 4.0);
}

vec4 opElongate( in vec3 p, in vec3 h )
{
    //return vec4( p-clamp(p,-h,h), 0.0 ); // faster, but produces zero in the interior elongated box
    
    vec3 q = abs(p)-h;
    return vec4( max(q,0.0), min(max(q.x,max(q.y,q.z)),0.0) );
}

float opExtrusion( in vec3 p, in float sdf, in float h )
{
    vec2 w = vec2( sdf, abs(p.z) - h );
    return min(max(w.x,w.y),0.0) + length(max(w,0.0));
}

// Box Function by IQ: https://iquilezles.org/articles/boxfunctions
vec2 iBox( in vec3 ro, in vec3 rd, in vec3 rad ) 
{
    vec3 m = 1.0/rd;
    vec3 n = m*ro;
    vec3 k = abs(m)*rad;
    vec3 t1 = -n - k;
    vec3 t2 = -n + k;
    return vec2( max( max( t1.x, t1.y ), t1.z ),
                 min( min( t2.x, t2.y ), t2.z ) );
}

//--------------------------------------

//---------------------------------------
// SDF BLEND & DOMAIN REPETITION: 
// https://mercury.sexy/hg_sdf/
//---------------------------------------

float pModPolar(inout vec2 p, float repetitions) 
{
    float angle = 2.*PI/repetitions;
    float a = atan(p.y, p.x) + angle/2.;
    float r = length(p);
    float c = floor(a/angle);
    a = mod(a,angle) - angle/2.;
    p = vec2(cos(a), sin(a))*r;
    // For an odd number of repetitions, fix cell index of the cell in -x direction
    // (cell index would be e.g. -5 and 5 in the two halves of the cell):
    if (abs(c) >= (repetitions/2.)) c = abs(c);
    return c;
}

// Repeat in two dimensions
vec2 pMod2(inout vec2 p, vec2 size) {
    vec2 c = floor((p + size*0.5)/size);
    p = mod(p + size*0.5,size) - size*0.5;
    return c;
}
//-----------------------------------------

//---------------------------------------------------------------
// MAIN
//---------------------------------------------------------------

#define ZERO (min(iFrame,0))
#define px 1./iResolution.y

// Materials
#define MAT_LEAVES 20
#define MAT_STEM 21
#define MAT_GROUND 30
#define MAT_GRASS 40
#define MAT_CLOUD 70
#define MAT_TREES 80
#define MAT_CASTLE_WHITE 90
#define MAT_CASTLE_FACADE 91
#define MAT_CASTLE_ROOF 100

#define MAT_BIFROST 110

#define MAT_GIRL_HAIR 120
#define MAT_GIRL_SKIN 121
#define MAT_GIRL_DRESS 122
#define MAT_GIRL_BOOTS 124
#define MAT_GIRL_FACE 127
#define MAT_GIRL_BLONDE 129

#define MAT_MUSHROOM_CAP1 140
#define MAT_MUSHROOM_CAP2 6
#define MAT_MUSHROOM_STEM 141

#define MAT_FLOWER_FACE 150
#define MAT_SMALL_FLOWER_PISTIL 151

#define MAT_BUNNY 160

#define MAT_GLOW 10001

#define RI_GRASSY_GROUND   (1u << 0)
#define RI_BIFROST         (1u << 1)
#define RI_ALICE           (1u << 2)
#define RI_BUNNY           (1u << 3)
// #define RI_MUSHROOM        (1u << 4)
#define RI_MUSHROOM1  (1u << 4)  
#define RI_MUSHROOM2  (1u << 10)

#define RI_TALKING_FLOWER  (1u << 5)
#define RI_FLOWER_BED      (1u << 6)
#define RI_CLOUDS          (1u << 7)
#define RI_GRASSY_MOUNTAIN (1u << 8)
#define RI_CASTLE          (1u << 9)

//---------------------------------------------------------------
// SDF Figures
//---------------------------------------------------------------

#   define opMin(_v, _m) res = (_v < res.x) ? vec2(_v, _m) : res
#   define opMinV(_v) res = (_v.x < res.x) ? _v : res

float sdPortalTorus(vec3 p)
{
    vec3 q = p - vec3(0.0, 0.1, 0.7);
    q.yz *= rot2d(PI/2.0);
    return sdTorus(q, vec2(1.0, 0.02));
}

void sdGrassyGround(vec3 p, inout vec2 res)
{
    float area = sdCylinder(p-vec3(0,-.17,0), vec2(1.2,0.001))-0.1;
    if(area-0.003 < res.x )
    {
        float distortion = (sin(10.*p.x)+cos(20.*p.z)) * 0.001;
        opMin(area-distortion, MAT_GRASS);
    }
}

//--------------- Bifrost Start ------------------
vec3 getRainbowColor(float t)
{
    t = clamp(t, 0.0, 1.0);
    float hue = t * 0.85;

    vec3 c = vec3(
        abs(hue*6.0-3.0)-1.0,
        2.0 - abs(hue*6.0-2.0),
        2.0 - abs(hue*6.0-4.0)
    );
    c = smoothstep(0.0, 1.0, clamp(c, 0.0, 1.0));

    c = mix(c, vec3(1.0), 0.15);

    return c;
}



vec3 worldToBifrost(vec3 p)
{
    p -= vec3(0.495, -0.08, .69);
    
    float t = clamp((p.z - BIFROST_Z_START) / (BIFROST_Z_END - BIFROST_Z_START), 0.0, 1.0);
    float envelope = sin(PI * t);
    float wiggle   = sin(BIFROST_LOOPS * PI * t);
    
    p.x += mix(0.0, BIFROST_GATE_X_CORRECTION, t);   // <-- new: straight path from start to gate
    p.x += BIFROST_SWAY_AMOUNT * envelope * wiggle;  // oscillation on top, still zero at both ends
    
    float bow = 4.0 * t * (1.0 - t);
    p.y -= mix(BIFROST_START_Y, BIFROST_END_Y, t) + BIFROST_BOW_HEIGHT * bow;
    
    return p;
}


vec3 getBifrostColor(vec3 p)
{
    vec3 q = worldToBifrost(p);
    
    float width = 0.25*(1.-.5*q.z);
    
    float colorT = (q.x + width * 0.5) / width;
    colorT = clamp(colorT, 0.0, 1.0);
    
    return getRainbowColor(colorT);
}

void sdBifrost(vec3 p, bool inside, inout vec2 res)
{
    if (!inside && p.z > 0.75) return;
    if (inside && p.z < 0.65) return;
    
    if(sdBox(p-BIFROST_CULL_CENTER, BIFROST_CULL_SIZE) < res.x)
    {
        vec3 q = worldToBifrost(p);
        vec3 boxSize = vec3(0.25*(1.-.56*q.z), 0.005*(1.-.9*q.z), 1.8) * 0.5;
        opMin((sdBox(q, boxSize)-.01) / BIFROST_LIPSCHITZ, MAT_BIFROST);   // <-- divide by Lipschitz bound
    }
}
//--------------- Bifrost End ---------------------


//--------------- Mountain Start -----------------
float getGroundHeight(vec2 p) {
    float h = (cos(1.9*p.x)+cos(1.9*p.y))*.6-.3;
    float distortion = (sin(15.*h)+cos(20.*p.y)) * 0.01;
    return h + distortion;
}

vec2 getPositionInXZGrid(vec3 p, float cellSize, float margin, vec2 seed)
{
    vec2 n = floor(p.xz / cellSize);
    vec2 o = hash22(n+seed);
    o = o * (1.0 - 2.0*margin) + margin;
    return (n + o) * cellSize;
}

// Rainforest by IQ: https://www.shadertoy.com/view/4ttSWf

void sdTrees(vec3 p, float innerBoundRadius, float outerBoundRadius, inout vec2 res)
{
    const float treeHeight = .025;
    const float treeWidth = .01;

    vec2 tp = getPositionInXZGrid(p, .15, .25, vec2(12,89));

    float d = length(tp);
    if (d > outerBoundRadius || d < innerBoundRadius) return;

    float base = getGroundHeight(tp);
    vec3 tree_center = vec3(tp.x, base+treeHeight*TREE_SIZE*.5, tp.y);
    vec3 q = p - tree_center;
    
    d = sdEllipsoid(q, vec3(treeWidth, treeHeight, treeWidth) * TREE_SIZE);
    if(d-0.002>res.x) return;
    
    d += sin(350.*p.y)*0.0008;
    opMin(d, MAT_TREES);
}

void sdGrassyMountain(vec3 p, inout vec2 res)
{
    float bound = sdCylinder(p-vec3(0,.23,0),vec2(1.,.33));
    if(bound < res.x)
    {
        float area = p.y-getGroundHeight(p.xz);
        area = smax(area,bound, .05);
        opMin(area, MAT_GRASS);
        
        if(max(bound, -sdCylinder(p, vec3(0,0,.58))) < res.x)
            sdTrees(p, .6, .95, res);
    }
}

//--------------- Mountain End -------------------

//--------------- Castle Start --------------------
float sdBattlement(vec3 p, float radius, vec2 crenelSize, float count)
{
    pModPolar(p.xz, count);
    return sdBox(p, vec3(radius, crenelSize));
}

vec2 sdCastleTower(vec3 p, float radius, float height, float floorCount, bool withBattlment)
{
    vec2 res = vec2( 1e10, 0.0 );
    vec3 top = p-vec3(0,height,0);
    
    float battH = radius * 0.7;
    float battY = height - battH;

    float r = radius;

    r = mix(r, r * 1.2, smoothstep(battY - 0.02, battY, p.y));
    
    if (floorCount > 1.0)
    {
        float y = p.y;
        opLimitedRepetition(y, battY/floorCount, int(floorCount));
        r = mix(r, r * 1.05, smoothstep(0.01, 0.0, abs(y)));
    }
    
    float base = max(sdCylinder(p, vec2(r, height)), -length(top)+radius+.01);
    base = withBattlment?max(base, -sdBattlement(top, radius*1.5, vec2(.015,.015), 6.)):base;
    
    opMin(base-.005, MAT_CASTLE_WHITE);
    
    vec3 q = top+vec3(0,.01,0);
    float h = 2.6*radius;
    float roof = sdCone(q, vec3(0.0), vec3(0.0,h,0.0), radius*.9, 0. );
    opMin(roof, MAT_CASTLE_ROOF);
    
    return res;
}

vec2 sdCastleTowers(vec3 p, float radius, float towerRadius, float towerHeight, float floorCount, float count, bool withBattlment)
{
    pModPolar(p.xz, count);
    p.x -= radius;
    return sdCastleTower(p, towerRadius, towerHeight, floorCount, withBattlment);
}

vec2 sdBuidlingBlock(vec3 p, vec4 rc, vec4 fc)
{
    float block = sdBox(p, vec3(.2,.22,.2));
    vec2 res = vec2(block-.005, MAT_CASTLE_WHITE);
    
    vec3 q = p;
    q.xy-=vec2(.135, .26);
    float blockRoof = sdTriPrism(q, vec2(rc.x,mix(rc.y,rc.z, q.y/rc.w)));
    opMin(blockRoof, MAT_CASTLE_ROOF);
    
    // unique facade!
    p-=vec3(.2,.10,0);
    q = p.zyx;
    float width = fc.y, height = fc.x;
    vec4 w = opElongate( q, vec3(0.,fc.x,0.02) );
    float facade = w.w+sdEllipsoid(w.xyz,vec3(fc.y,fc.y,0.01));
    opMin(facade, MAT_CASTLE_FACADE);
    
    //p.y+=.04;
    //opMin(opExtrusion(p.zyx-vec3(0,0,.011), sdTunnel(p.zy, vec2(.02,.04)), .02), MAT_CASTLE_ROOF); // Paint instead
    
    return res;
}

void sdMainBuilding(vec3 p, inout vec2 res)
{
    opMin(max(length(p)-.45, p.y-.02), MAT_CASTLE_WHITE);
    float boundCylinder = sdCylinder(p-vec3(0,.30,0),vec2(.4,.3));
    if(boundCylinder < res.x)
    {
        vec3 q = p;
        q.xz *= rot2d(PI/2.);
        float faceId = pModPolar(q.xz, 6.);
        q.x -= .1;
        
        opMinV(sdBuidlingBlock(q, vec4(.08,.11,.045,.08), vec4(.15,.045,2.,.005)));
        
        opMinV(sdCastleTowers(p, .35, .04, .35, 3., 6., true));
        
        q = p;
        q.x = abs(q.x)-.22;
        q.z = q.z-.1;
        opMinV(sdCastleTower(q, .055, .45, 6., true));
        
        p.xz*=rot2d(PI/2.);
        opMinV(sdBuidlingBlock(p-vec3(0,.17,0), vec4(.1,.17,.08,.17), vec4(.13,.08,1.5,0.02)));
    }
}

void sdCastle(vec3 p, inout vec2 res)
{
    p-=vec3(0,.55,0);
    
    if(length(p)-.7 < res.x && p.y>-.1)
    {
        float fort = max(sdCylinder(p, vec2(.6,.05)),-length(p)+.59);
        fort = max(fort, -sdBattlement(p-vec3(0,.053,0),.7,vec2(.02), 50.));
        
        {
            vec3 q=p+vec3(0,0,.6);
            vec4 w = opElongate( q, vec3(-0.01,0.03,0.0) );
            float gateBuilding = w.w+opExtrusion( w.xyz,max(sdHexagon(w.yx,.08),-sdTunnel(q.xy+vec2(0,-.02),vec2(.04,.07))),.03);
            opMin(gateBuilding-.01, MAT_CASTLE_WHITE);
            opMin(sdBox(q,vec3(.07,.07,.005)), MAT_CASTLE_ROOF);
        }
        
        opMin(fort-.005, MAT_CASTLE_WHITE);
        
        opMinV(sdCastleTowers(p, .6, .03, .09, 1., 6., false));
        
        sdMainBuilding(p, res);
    }
}

#define COLOR_CASTLE_ROOF vec3(0.11, 0.306, 0.502)

void paintCastleFacade(vec3 p, inout vec3 FinalColor)
{
    p-=vec3(0, .56, 2.2);
    p.xz *= rot2d(PI/2.);
    pModPolar(p.xz, 6.);
    float d = sdTunnel(p.zy, vec2(.02,.04));
    FinalColor = mix(FinalColor, COLOR_CASTLE_ROOF, smoothstep(px, 0.,d));
}
//--------------- Castle End ----------------------

//--------------- Clouds Start --------------------
vec2 sdCloud(vec3 p, vec2 seed, float cloudRadius)
{
    p.y += 1.;

    vec2 res = vec2(1000.,0);
    float bound = sdCylinder(p-vec3(0,1.,0),
                             vec2(cloudRadius + 0.35, 1.2));
    if (bound > .5) return vec2(bound, 0);
    
    const float spacing = 0.8;
    const float cellSize = 0.8;

    float rx = hash12(seed + vec2(.1, 0));
    float rz = hash12(seed + vec2(0, .1));
    vec2 gridOffset = vec2(mix(-0.4, -0.1, rx), mix(-0.4, -0.1, rz)) * cellSize;

    vec2 q_xz   = (p.xz + gridOffset) / spacing;
    vec2 cellId = floor(q_xz);


    for (int ix = -1; ix <= 1; ++ix) {
        for (int iz = -1; iz <= 1; ++iz) {
            vec2 neighborId = cellId + vec2(float(ix), float(iz));

            vec2 basePos = (neighborId + 0.5) * spacing - gridOffset;

            float baseDist = length(basePos);
            if (baseDist > cloudRadius) continue;
            
            float baseNRadius = baseDist / cloudRadius;

            float hx = hash12(neighborId + vec2(12.34, 56.78));
            float hz = hash12(neighborId + vec2(78.91, 23.45));
            float hy = hash12(neighborId + vec2(45.67, 89.01));
            vec3 jitter = vec3(hx, hy, hz) * 2.0 - 1.0;
            jitter.xz *= (spacing * 0.25);

            vec2 worldPos = basePos + jitter.xz;
            
            worldPos *= (1.0 - baseNRadius * 0.25);
            jitter.y *= (1.0 - baseNRadius * 0.5) * .4;

            float distFromCenter = length(worldPos);
            if (distFromCenter > cloudRadius) continue;

            float radius = mix(1.21, .34, distFromCenter / cloudRadius);

            vec3 sphereCenter = vec3(worldPos.x, radius + jitter.y, worldPos.y);

            float dist = length(p - sphereCenter) - radius;
            opMin(smin(res.x, dist, .015), MAT_CLOUD);
        }
    }
    
    res = res.x > 999. ? vec2(bound + 0.7, 0) : res;

    return res;
}

void sdCloudLayer(vec3 p, float scale, inout vec2 res)
{
    p.xz *= rot2d(CLOUD_ROTATION_ANGLE);   // <-- rotate around the island's Y axis first
    p*=scale;
    float bound = max(sdCylinder(p-vec3(0,2.1,0),vec2(13.5,2.7)),-sdCylinder(p, vec3(0,0,7.)));
    if(bound < res.x)
    {
        const float layerSpacing = 2.6;
        const int numLayers = 2;
        
        p.y-=.8;
        float layerId = opLimitedRepetition(p.y, layerSpacing, numLayers);
        
        float angleId = pModPolar(p.xz, 12.);
    
        vec2 seed = vec2(angleId, layerId);
    
        float showHash = hash12(seed + vec2(160.0, 123.0));
        if (showHash < 0.6) return;
    
        p.x -= 9.0 + 2.0 * hash12(seed + vec2(12.34, 56.78)) - layerId*.2;
    
        float cloudRadius = mix(1.0, 1.8, hash12(seed + vec2(0.5, 0)));
    
        vec2 clouds = sdCloud(p, seed, cloudRadius);
        clouds.x/=scale;
        opMinV(clouds);
    }
}
//--------------- Clouds End ----------------------

//--------------- Alice Start ----------------------
// #define ALICE_SCALE 1.9

vec3 worldToAlice(vec3 p)
{
    p*=ALICE_SCALE;
    p-=vec3(0,ALICE_Y_OFFSET,-.1);
    p.xz *= rot2d(ALICE_SPIN_ANGEL);   // <-- spin around her local Y axis
    return p;
}

void sdAlice(vec3 p, inout vec2 res)
{   
    p = worldToAlice(p);
    float bound = sdCylinder(p-vec3(0, ALICE_LOCAL_CENTER,0),vec2(.105, ALICE_LOCAL_BOUND));
    if(bound > res.x) return;
    
    // Head
    {
        if(p.y>-.06)
        {
            vec3 headP = p;
            float head = smin(length(headP-vec3(0,.01,0))-.0265, sdEllipsoid(headP-vec3(-.015, -.022, 0),vec3(.011, .012,.017)), .009);
            
            vec3 eyeSocketP = headP-vec3(-.04, -.005, 0);
            eyeSocketP.z = abs(eyeSocketP.z)-.01;
            head = smax(head, -length(eyeSocketP)+.0011, .02);
            
            vec3 noseP = headP-vec3(-.032, -.0175, 0);
            head = smin(head, sdCapsule(noseP,vec3(0,0,0), vec3(.0055,.01,0), .001 ), .001);
            
            vec3 jawP = headP-vec3(-.0212,-.036, 0);
            jawP.z = abs(jawP.z)-.0006;
            head = smin(head, sdCapsule(jawP,vec3(0,0,0), vec3(.017,.009,.01), .004 ), .003);
            
            vec3 neckP = p-vec3(.000,-.05, 0);
            head = min(head, sdCapsule(neckP,vec3(.002,0,0), vec3(.0,.02,.0), .01));
            
            opMin(head, MAT_GIRL_FACE);
        }
        
        if(p.y>-.11)
        {
            vec3 hairP = p;
            float hair = abs(sdRoundCone(hairP, vec3(-0.001,.0001,0), vec3(0, -.07, 0), .0285, .0385))-.007;
            hair+=.0015*sin(60.*hairP.y-3.8)+.00038*sin(200.*hairP.y);
            
            hairP -= vec3(-.06, -.032, 0);
            float hairCut = sdRoundBox(hairP, vec3(.05, .08,.027), .02);
            hairCut = max(hairCut, hairP.y-.047+abs(.024*sin(50.*hairP.z-.1)));
            
            hair = smax(hair, -hairCut, .02);
            opMin(hair, MAT_GIRL_BLONDE);
        }
    }
    
    // Dress
    if(p.y<-.04&&p.y>-.35)
    {
        vec3 dressP = p-vec3(.006,0,0);
        
        vec3 topP = dressP-vec3(0,-.123, 0);
        float w = mix(.026,.0001,clamp((topP.y-.05)/-.1,.0,1.));
        float t = .0001+.007*abs(sin(30.*topP.y+0.9));
        float dress = sdBox(topP, vec3(t, .05, w))-.025;
        
        vec3 skirtP = dressP-vec3(0,-.23, 0);
        float l = clamp((skirtP.y-.1)/-.2,.0,1.)+.3*sin(18.*skirtP.y+1.97)+.03*sin(50.*skirtP.y-.5);
        float r = mix(.009,.09,l);
        r += mix(1e-5,.005,l)*sin(8.*atan(skirtP.z/skirtP.x));
        float belt = smoothstep(.065, .07, skirtP.y) * smoothstep(.085, .074, skirtP.y);
        r = mix(r, .023, belt);
        r*= max(0., min(1.-abs(skirtP.x)/.35, 1.-abs(skirtP.z)/1.));
        float skirt = sdCylinder(skirtP, vec2(r,.1))-.01;
        dress = min(dress, skirt);
        
        vec3 sleevesP = dressP-vec3(0,-.07,0);
        sleevesP.z = abs(sleevesP.z)-.047;
        float sleeves = sdSphere(sleevesP, .02);
        dress = min(dress, sleeves);
        
        vec3 collarP = dressP-vec3(0,-.034,0);
        float collar = sdCone(collarP,vec2(1,.8),.025)-.0015;
        collarP.z = abs(collarP.z);
        collarP.x+=.017;
        collarP.zx*=rot2d(PI/4.);
        collar = smax(collar, -collarP.x, .005);
        dress = min(dress, collar);
        
        opMin(dress, MAT_GIRL_DRESS);
    }
    
    // Legs
    if(p.y<-.33)
    {
        vec3 legsP = p-vec3(.006,-.45,0);
        float r = .009+.004*sin(32.*legsP.y-1.5);
        float legs = min(sdVerticalCapsule(legsP-vec3(0,0,-.012),.12,r), 
                            sdVerticalCapsule(legsP-vec3(-.017,0,.012),.12,r));
        opMin(legs, MAT_CLOUD);
        
        float foot = min(sdCapsule(legsP, vec3(0,0,-.012), vec3(-.025,0,-.025), .01),
                            sdCapsule(legsP, vec3(-.017,0,.012), vec3(-.04,0,.02), .01));
        opMin(foot, MAT_GIRL_BOOTS);
    }
    
    // Arms
    if(p.y<-.06&&p.y>-.16)
    {
        vec3 armsP, armsBaseP = armsP = p-vec3(.006,-.063,0);
        armsP.z = abs(armsP.z)-.047;
        
        float r1 = .0085+.0008*sin(100.*armsP.y-.05),
              r2 = .008+.0014*sin(95.*armsP.z+1.2);
        float arms = sdCapsule(armsP, vec3(0,0,.005), vec3(0,-.085,.01),r1);
        arms = smin(arms, sdCapsule(armsP, vec3(-.005,-.083,.007), vec3(-.05,-.07,-.03),r2), .001);
        vec3 handsP = armsBaseP-vec3(-.05,-.07,.0018);
        float hands = min(sdEllipsoid(handsP, vec3(.012,.008,.022)), sdSphere(handsP-vec3(-0.001,-.0045,-.004),.01));
        arms = min(arms, hands);
        
        opMin(arms, MAT_GIRL_SKIN);
    }
    
    res.x/=ALICE_SCALE;
}

void _paintFace(vec3 p, inout vec3 FinalColor)
{   
    float d;
    vec2 eyeP = p.yz - vec2(-.009,0);
    eyeP.y = abs(eyeP.y)-.01;
    d = max(abs(length(eyeP)-.005)-.0005, -eyeP.x+.0025);
    FinalColor = mix(FinalColor, vec3(0), smoothstep(px, 0.,d));
    
    vec2 mouthP = p.yz - vec2(-.0173,0);
    float ud = length(mouthP)-.01;
    d = max(abs(ud)-.0004, mouthP.x+.007);
    d = min(d, max(length(mouthP-vec2(-.017,0))-.01, ud));
    
    FinalColor = mix(FinalColor,vec3(0.7608, 0.1176, 0.3373), smoothstep(px, 0.,d));
}

void paintFace(vec3 p, inout vec3 FinalColor)
{
    p = worldToAlice(p);
    
    _paintFace(p, FinalColor);
}

// Triplanar/Boxmap Mapping by IQ : https://www.shadertoy.com/view/MtsGWH
vec3 paintGirlDress(vec3 p, vec3 n, float scale)
{
    vec3 scaledP = p*scale;
    
    float r=.2,s=1e-4;
    
    float x = smoothstep(s,-s,length(fract(scaledP.yz)-.5)*2.-r);
    float y = smoothstep(s,-s,length(fract(scaledP.xz)-.5)*2.-r);
    float z = smoothstep(s,-s,length(fract(scaledP.xy)-.5)*2.-r);
    
    vec3 m = pow(abs(n),vec3(10.));
    
    return vec3(.35)*(x*m.x + y*m.y + z*m.z) / (m.x + m.y + m.z + 1e-5);
}

//--------------- Alice End ----------------------

//--------------- Mushroom Start -----------------

// #define MUSHROOM_POS vec3(0,-.06,-.8)
#define MUSHROOM_HEIGHT .42
// #define MUSHROOM_SCALE MU

void worldToMushroom1(inout vec3 p)
{
    p -= MUSHROOM1_POS;
    p *= MUSHROOM1_SCALE;
}

void sdMushroom1(vec3 p, inout vec2 res) {
    worldToMushroom1(p);
    float h = MUSHROOM_HEIGHT;
    float bound = sdCylinder(p-vec3(0,.3,0), vec3(0,0,.45));
    if(bound > res.x) return;
    if(p.y<.80&&p.y>.25) {
        vec3 topP = p - vec3(0,h,0);
        float top = sdSphere(topP-vec3(0,.1,0), .08);
        top = smin(top, sdEllipsoid(topP, vec3(0.3,0.05,0.3)), .08);
        top = smax(top, -sdSphere(topP-vec3(0,-.55,0), .5), .08);
        opMin(top, MAT_MUSHROOM_CAP1);
    }
    if(p.y<.38&&p.y>-.06) {
        vec3 stemP = p;
        float t = stemP.y / h-.6;
        stemP.xz -= t*t*vec2(.12, .05);
        float stem = sdVerticalCapsule(stemP, h, .05+.025*smoothstep(1.,0.,stemP.y/h));
        opMin(stem, MAT_MUSHROOM_STEM);
    }
}

void paintMushroomCap1(vec3 p, vec3 n, inout vec3 color, inout vec3 shadowColor) {
    worldToMushroom1(p);
    color = n.y > -.85 ? vec3(0.9, 0.0, 0.25) : vec3(0.95, 0.95, 0.9);
    shadowColor = n.y > -.85 ? vec3(0.85, 0.0, 0.25) : vec3(0.85, 0.85, 0.8);
    if(n.y > -0.85) {
        vec2 cell = pMod2(p.xz, vec2(MUSHROOM1_SPOT_DENSITY));
        if(length(cell*MUSHROOM1_SPOT_DENSITY)<.28) {
            float r = mix(MUSHROOM1_SPOT_SIZE_MIN, MUSHROOM1_SPOT_SIZE_MAX, hash12(cell));
            color = mix(color, vec3(1.), smoothstep(px, 0., length(p.xz)-r));               }
    }
}

void worldToMushroom2(inout vec3 p)
{
    p -= MUSHROOM2_POS;
    p *= MUSHROOM2_SCALE;
}


void sdMushroom2(vec3 p, inout vec2 res) {
    worldToMushroom2(p);
    float h = MUSHROOM_HEIGHT;
    float bound = sdCylinder(p-vec3(0,.3,0), vec3(0,0,.45));
    if(bound > res.x) return;
    if(p.y<.80&&p.y>.25) {
        vec3 topP = p - vec3(0,h,0);
        float top = sdSphere(topP-vec3(0,.1,0), .08);
        top = smin(top, sdEllipsoid(topP, vec3(0.3,0.05,0.3)), .08);
        top = smax(top, -sdSphere(topP-vec3(0,-.55,0), .5), .08);
        opMin(top, MAT_MUSHROOM_CAP2);
    }
    if(p.y<.38&&p.y>-.06) {
        vec3 stemP = p;
        float t = stemP.y / h-.6;
        stemP.xz -= t*t*vec2(.12, .05);
        float stem = sdVerticalCapsule(stemP, h, .05+.025*smoothstep(1.,0.,stemP.y/h));
        opMin(stem, MAT_MUSHROOM_STEM);
    }
}

void paintMushroomCap2(vec3 p, vec3 n, inout vec3 color, inout vec3 shadowColor) {
    worldToMushroom2(p);
    color = n.y > -.85 ? vec3(0.95, 0.1, 0.0) : vec3(0.95, 0.95, 0.9);
    shadowColor = n.y > -.85 ? vec3(0.6, 0.05, 0.0) : vec3(0.85, 0.85, 0.8);
    if(n.y > -0.85) {
        vec2 cell = pMod2(p.xz, vec2(MUSHROOM2_SPOT_DENSITY));
        if(length(cell*MUSHROOM2_SPOT_DENSITY)<.28) {
            float r = mix(MUSHROOM2_SPOT_SIZE_MIN, MUSHROOM2_SPOT_SIZE_MAX, hash12(cell));
            color = mix(color, vec3(1.), smoothstep(px, 0., length(p.xz)-r));               
            }
        }
    }

// void worldToMushroom(inout vec3 p)
// {
//     p -= MUSHROOM_POS;
//     p.x = abs(p.x)-.7;
//     p *= MUSHROOM_SCALE;
// }

// void sdMushroom(vec3 p, inout vec2 res) 
// {
//     worldToMushroom(p);
//     float h = MUSHROOM_HEIGHT;
    
//     float bound = sdCylinder(p-vec3(0,.3,0),vec3(0,0,.31));
//     if(bound > res.x) return;
    
//     if(p.y<.80&&p.y>.25)
//     {
//         vec3 topP = p - vec3(0,h,0);
//         float top = sdSphere(topP-vec3(0,.1,0), .08);
//         top = smin(top, sdEllipsoid( topP, vec3(0.3,0.05,0.3) ), .08);
//         top = smax(top, -sdSphere(topP-vec3(0,-.55,0), .5), .08);
//         opMin(top, MAT_MUSHROOM_CAP);
//     }
    
//     if(p.y<.38&&p.y>-.06)
//     {
//         vec3 stemP = p;
//         float t = stemP.y / h-.6;
//         stemP.xz -= t*t*vec2(.12, .05);
//         float stem = sdVerticalCapsule(stemP, h, .05+.025*smoothstep(1.,0.,stemP.y/h));
//         opMin(stem, MAT_MUSHROOM_STEM);
//     }
// }

// void paintMushroomCap(vec3 p, vec3 n, inout vec3 color, inout vec3 shadowColor)
// {
//     float side = sign(p.x);
//     worldToMushroom(p);

//     vec3 topColor, topShadowColor;
//     if(side<0.) {
//         topColor = vec3(0.9, 0.0, 0.25);
//         topShadowColor = vec3(0.85,0.0,0.25);
//     }
//     else {
//         topColor = vec3(0.95,0.1,0.0);
//         topShadowColor = vec3(0.6,0.05,0.0);
//     }
//     color = n.y > -.85 ? topColor: vec3(0.95, 0.95, 0.9);
//     shadowColor = n.y > -.85 ? topShadowColor: vec3(0.85,0.85,0.8);

//     if (n.y > -0.85) 
//     {
//         vec2 cell = pMod2(p.xz, vec2(.1));
//         if(length(cell*.1)<.28)
//         {
//             float r = mix(.01, .025, hash12(cell));
//             color = mix(color,vec3(1.),smoothstep(px,0.,length(p.xz)-r));
//         }
//     }
// }
//--------------- Mushroom End -------------------

//------------ Talkign Flower Start --------------
// #define TALKING_FLOWER_POS vec3(-1.,-.05,-.3)
#define TALKING_FLOWER_ROTATION -PI/2.
// #define TALKING_FLOWER_SCALE 1.2
#define TALKING_FLOWER_HEIGHT .42
#define TALKING_FLOWER_FACE_Y_TUNE 0.07


vec3 worldToFlowerFace(vec3 p)
{
    p -= TALKING_FLOWER_POS;
    p *= TALKING_FLOWER_SCALE;
    p.xz*=rot2d(TALKING_FLOWER_ROTATION);
    p -= vec3(0,TALKING_FLOWER_HEIGHT,-.1);
    p.y += TALKING_FLOWER_FACE_Y_TUNE;
    return p;
}



void sdTalkingFlowerPlant(vec3 p, inout vec2 res)
{   
    p -= TALKING_FLOWER_POS;
    p *= TALKING_FLOWER_SCALE;              
    p.xz*=rot2d(TALKING_FLOWER_ROTATION);
    float h = TALKING_FLOWER_HEIGHT;
    
    float bound = sdCylinder(p-vec3(0,.2,-.06),vec3(0,0,.23));
    if(bound > res.x) return;

    vec3 topP = p - vec3(0,h,-.05);
    if(p.y<.5&&p.y>-.03)
    {
        vec3 stemP = p;
        stemP.z -= .06*sin(12.*stemP.y-1.5);
        float stem = sdVerticalCapsule(stemP, h, .01);
        
        stem = min(stem, max(sdRoundCone(topP,vec3(0,0,-.05),vec3(0,0,.01), .08, .035), -topP.z-.03));
        opMin(stem, MAT_STEM);
    }

    if(p.y<.75&&p.y>.19)
    {
        float face = sdEllipsoid( topP-vec3(0,0,-.04), vec3(0.08,0.08,0.022));
        opMin(face, MAT_FLOWER_FACE);
        
        topP.z-=-.035;
        topP.xy *= rot2d(FLOWER_PETAL_ROTATION);
        pModPolar(topP.xy, 10.);
        topP.x-=.145;
        float petals = sdEllipsoid( topP, vec3(.08,.045,.01));
        petals-=abs(sin(50.*topP.y-0.))*.002*clamp((.06-topP.x)/.08,0.,1.);
        opMin(petals, MAT_MUSHROOM_STEM);
    }
    
    if(p.y<.13&&p.y>-.03)
    {
        vec3 leavesP = p-vec3(0,-.01,-.06);
        pModPolar(leavesP.xz, 4.);
        leavesP.xy*=rot2d(-PI/3.5);
        float leafLength = .1, t = leavesP.x/leafLength -.5;
        leavesP.x-=leafLength;
        leavesP.y += t*t*.05;
        float leaves = sdEllipsoid( leavesP, vec3(leafLength,.015,.045));
        leaves-=abs(sin(70.*leavesP.z))*.005*clamp((leafLength-.02-leavesP.x)/leafLength,0.,1.);
        opMin(leaves, MAT_LEAVES);
    }
    res.x /= TALKING_FLOWER_SCALE;    
}

void paintFlowerFace(vec3 p, inout vec3 color)
{
    p = worldToFlowerFace(p);
    
    _paintFace((p.zyx-vec3(0,.12,0))*.34, color);
}
//------------ Talkign Flower End ----------------

//---------------- Bunny Start -------------------
// #define BUNNY_POS vec3(-.9,0,BUNNY_Z_OFFSET) //original z = .4
#define BUNNY_ROTATION -PI/4.
// #define BUNNY_SCALE 1.2

void worldToBunny(inout vec3 p)
{
    p *= BUNNY_SCALE;
    p.xz*=rot2d(BUNNY_ROTATION);
    p -= BUNNY_POS;
}
void sdBunny(vec3 p, inout vec2 res)
{   
    worldToBunny(p);
    float bound = sdCylinder(p-vec3(0, BUNNY_LOCAL_CENTER, -.02),vec3(BUNNY_LOCAL_BOUND, 0, 1.1));
    if(bound > res.x) return;
    
    vec3 bodyP = p-vec3(0,.1,0);
    float bunny = sdRoundCone(bodyP,vec3(0),vec3(0,.24,-.1),.2,.13), t;
    
    if(p.y<.4&&p.y>-.09)
    {
        bunny = smin(bunny, sdSphere(bodyP-vec3(0,-.01,-.063), .15),.01);
        
        vec3 legsP = p;
        legsP.x = abs(legsP.x)-.1;
        bunny = smin(bunny, sdSphere(legsP-vec3(-0.05,0,.03), .14), .03);
        bunny = smin(bunny, sdRoundCone(legsP,vec3(-.04,0.01,.01),vec3(.06,.07,-.1),.16,.09), .001);
        bunny = smin(bunny, sdRoundBox(legsP-vec3(0.045,-.057,-.1),vec3(.05,.038,.08),.038), .003);
        
        bunny = min(bunny, sdSphere(bodyP-vec3(0,-.1,.2), .08 * BUNNY_TAIL_SCALE));
        
        vec3 armsBaseP = p - vec3(0,.25,0);
        float armLength = .2;

        // Right arm — static, unchanged pose
        vec3 armsP_R = armsBaseP;
        armsP_R.x -= .13;
        t = armsP_R.z/armLength + .5;
        armsP_R.xy += t*t*vec2(.11,-.07);
        float armR = sdCapsule(armsP_R, vec3(0), vec3(0,0,-armLength), .05);

        // Left arm — waving
        vec3 armsP_L = armsBaseP;
        armsP_L.x = -armsP_L.x - .13;
        armsP_L.yz *= rot2d(BUNNY_WAVE_ANGLE * BUNNY_WAVE_RANGE_SCALE);
        t = armsP_L.z/armLength + .5;
        armsP_L.xy += t*t*vec2(.11,-.07);
        float armL = sdCapsule(armsP_L, vec3(0), vec3(0,0,-armLength), .05);

        bunny = smin(bunny, min(armR, armL), .003);
    }
    if(p.y<BUNNY_HEAD_Y_MAX && p.y>.25)
    {
        vec3 headP = p-vec3(0,.48,-.13);
        float head = sdSphere(headP, .17);
        
        vec3 cheeksP = headP-vec3(0,-.065,-.13);
        float l = .22;
        t = cheeksP.x/l;
        cheeksP.yz += t*t*vec2(-.05,-.18);
        head = smin(head, sdCapsule(cheeksP,vec3(-l/2.,0,0),vec3(l/2.,0,0), .05), .015);
        
        vec3 noseP = headP-vec3(0,-.04,-.17);
        head = smin(head, sdSphere(noseP-vec3(0,0,-.005), .01), .01);
        
        vec3 earsP = headP-vec3(0,.08,.05);
        earsP.x = abs(earsP.x)-.07;
        float ears = smax(abs(sdVesicaSegment(earsP, vec3(0), vec3(.1,.36,0)*BUNNY_EAR_SCALE, .065*BUNNY_EAR_SCALE) - .02*BUNNY_EAR_SCALE) - .015*BUNNY_EAR_SCALE, -earsP.z-.02*BUNNY_EAR_SCALE, .02*BUNNY_EAR_SCALE);
        head = smin(head, ears, .005);    
        bunny = smin(bunny, head, .007);
    }
    
    opMin(bunny/BUNNY_SCALE, MAT_BUNNY);
}

void paintBunny(vec3 p, inout vec3 color)
{
    worldToBunny(p);
    p-=vec3(0,.48,-.13);
    
    if(p.z<0.)
    {
        float d;
        vec2 eyeP = p.xy;
        eyeP.x = abs(eyeP.x)-.06;
        d = max(abs(length(eyeP)-.02)-.004, -eyeP.y+.0025);
        color = mix(color, vec3(0), smoothstep(px,-px,d));
        
        vec2 noseP = p.xy-vec2(0,-.057);
        d = sdPie(noseP,vec2(.84,.54), 0.02)-.005;
        color = mix(color, vec3(1.0,0.35,0.25), smoothstep(px,-px,d));
        
        vec2 mouthP = p.xy-vec2(0,-.064);
        mouthP.x = abs(mouthP.x)-.01;
        d = max(abs(length(mouthP-vec2(.01,0))-.025)-.003, mouthP.y+.008);
        color = mix(color, vec3(1.0,0.35,0.25)*.4, smoothstep(px,-px,d));
    }
}
//---------------- Bunny End ---------------------

//------------- Flower Bed Start -----------------
void sdBedFlower(vec3 p, inout vec2 res) // Merge with talking flower
{
    p *= FLOWER_BED_SIZE;   
    opMin(sdSphere(p, .005)/.5,MAT_SMALL_FLOWER_PISTIL);
    
    pModPolar(p.xz, 7.);
    p.x-=.01;
    p.y-=.001;
    p.xy*=rot2d(-PI/12.);
    float petals = sdEllipsoid(p,vec3(.009,.001,.0045));
    opMin(petals/.5, MAT_MUSHROOM_STEM);
    res.x /= FLOWER_BED_SIZE;   
}

void sdFlowerBed(vec3 p, float radius, inout vec2 res)
{
    if(p.y>-.02||p.y<-.07||length(p)>1.3) return;

    vec2 tp = getPositionInXZGrid(p,.35,.1,vec2(11,33));

    float d = length(tp);
    if (d > radius) return;
    
    sdBedFlower(p-vec3(tp.x,-.065,tp.y), res);
}
//-------------- Flower Bed End ------------------

//--------------------------------------
// MAIN SDF 
//--------------------------------------
#define isVisible(mask) (riFlags & mask) != 0u
vec2 mainWorld(in vec3 p, in uint riFlags)
{
    vec2 res = vec2(sdTorus(p-vec3(0,-.18,.0),vec2(1.215,0.09)),MAT_GROUND);
    
    float bound = sdCylinder(p-vec3(0,.3,0),vec2(1.31, max(0.5, ALICE_WORLD_BOUND)));
    if(bound > res.x) return res;
    
    if(isVisible(RI_GRASSY_GROUND)) sdGrassyGround(p, res);
    
    if(isVisible(RI_BIFROST)) sdBifrost(p, false, res);
    
    if(isVisible(RI_ALICE)) sdAlice(p, res);
    
    if(isVisible(RI_BUNNY)) sdBunny(p, res);
    
    // if(isVisible(RI_MUSHROOM)) sdMushroom(p, res);
    if(isVisible(RI_MUSHROOM1)) sdMushroom1(p, res);

    if(isVisible(RI_MUSHROOM2)) sdMushroom2(p, res);
    
    if(isVisible(RI_TALKING_FLOWER)) sdTalkingFlowerPlant(p, res);
    
    if(isVisible(RI_FLOWER_BED)) sdFlowerBed(p, 1.2, res);
    
    return res;
}

vec2 portalWorld(in vec3 q, in uint riFlags)
{
    vec3 p = q-vec3(0,-.05,2.2);
    vec2 res = vec2(sdTorus(p-vec3(0,-.1,.0),vec2(1.,.09)),MAT_GROUND);
    
    if(isVisible(RI_BIFROST)) sdBifrost(q, true, res);
    
    if(isVisible(RI_CLOUDS)) sdCloudLayer(p-vec3(0,.05,0), 10., res);
    
    if(isVisible(RI_GRASSY_MOUNTAIN)) sdGrassyMountain(p, res);
    
    if(isVisible(RI_CASTLE)) sdCastle(p, res);
    
    return res;
}

vec2 map(in vec3 p, in bool inside, in uint riFlags)
{
    return !inside? mainWorld(p, riFlags): portalWorld(p, riFlags);
}

float portal_intersect(vec3 ro, vec3 rd)
{
    const float planeZ = 0.7;
    const float radius = 0.98;

    if (abs(rd.z) < 1e-6) return 1e5; 
    float t = (planeZ - ro.z) / rd.z;
    if (t <= 0.0) return 1e5;

    vec3 hit = ro + rd * t;

    vec2 center2D = hit.xy - vec2(0.0, 0.1);
    if (length(center2D) < radius)
        return t;

    return 1e5;
}

// ----- Ray Intersection with Object Bounding Box : Start -----
bool rayIntersectsBox(vec3 ro, vec3 rd, vec3 boxCenter, vec3 boxSize, float tmax, inout vec2 tb)
{
    tb = iBox(ro-boxCenter,rd,boxSize);
    
    return (tb.x < tb.y && tb.y > 0.0 && tb.x < tmax);
}

uint getRayIntersectionFlags(vec3 ro, vec3 rd, float tmax)
{
    vec2 tb;
    uint riFlags = 0u;
    
    if(rayIntersectsBox (ro,rd, vec3(0,-.11,0), vec3(1.35,0.075,1.3), tmax, tb))
        riFlags |= RI_GRASSY_GROUND;
        
    if(rayIntersectsBox(ro,rd, BIFROST_CULL_CENTER, BIFROST_CULL_SIZE, tmax, tb))
        riFlags |= RI_BIFROST;

    if (rayIntersectsBox(ro,rd,vec3(0,.47,1.),vec3(max(1.31, 0.35/ALICE_SCALE), .72, 2.35), tmax, tb))    
        riFlags |= RI_ALICE;
    
    // if(rayIntersectsBox(ro,rd, vec3(-.73, BUNNY_Y_OFFSET+0.09, .31), 
    //    vec3(max(1.21, 0.35/BUNNY_SCALE), max(1.1*BUNNY_SCALE, 1.1/BUNNY_SCALE), .21), tmax, tb))
    //     riFlags |= RI_BUNNY;


    if(rayIntersectsBox(ro,rd, vec3(-.73, BUNNY_Y_OFFSET+0.09, .31), 
        vec3(max(1.21, 0.35/BUNNY_SCALE) + BUNNY_TAIL_EXTRA_REACH/BUNNY_SCALE, 
        max(1.1*BUNNY_SCALE, 1.1/BUNNY_SCALE) + BUNNY_EAR_EXTRA_REACH/BUNNY_SCALE, 
        .21 + (BUNNY_EAR_EXTRA_REACH + BUNNY_TAIL_EXTRA_REACH)/BUNNY_SCALE), 
        tmax, tb))
                riFlags |= RI_BUNNY;

    if(rayIntersectsBox(ro, rd, 
       vec3(-0.7, MUSHROOM1_POS.y + 0.4/MUSHROOM1_SCALE, -.8), 
       vec3(.45/MUSHROOM1_SCALE, .85/MUSHROOM1_SCALE, .45/MUSHROOM1_SCALE), tmax, tb))
        riFlags |= RI_MUSHROOM1;

    if(rayIntersectsBox(ro, rd, 
       vec3(0.7, MUSHROOM2_POS.y + 0.4/MUSHROOM2_SCALE, -.8), 
       vec3(.45/MUSHROOM2_SCALE, .85/MUSHROOM2_SCALE, .45/MUSHROOM2_SCALE), tmax, tb))
        riFlags |= RI_MUSHROOM2;    

    vec3 flowerBoxHalf = vec3(.22,.34,.23) * (1.2/TALKING_FLOWER_SCALE);
    vec3 flowerBoxCenter = vec3(-.94, -.09 + flowerBoxHalf.y, -.3);  // -.09 = original tuned ground-level bottom
    if(rayIntersectsBox(ro,rd, flowerBoxCenter, flowerBoxHalf, tmax, tb))
        riFlags |= RI_TALKING_FLOWER;    
    
    if(rayIntersectsBox(ro,rd, vec3(0,-.065,-.15), vec3(1.2,.02,1.), tmax, tb))   // <-- add this back
        riFlags |= RI_FLOWER_BED;


    if(rayIntersectsBox(ro,rd, vec3(0,.26,2.2), vec3(1.2,.27,1.12), tmax, tb))
        riFlags |= RI_CLOUDS;
        
    if(rayIntersectsBox(ro,rd, vec3(0,.28,2.2), vec3(1.,.35, 1.), tmax, tb))
        riFlags |= RI_GRASSY_MOUNTAIN;
        
    if(rayIntersectsBox(ro,rd, vec3(0,.72,2.2),  vec3(.66,.36,.66), tmax, tb))
        riFlags |= RI_CASTLE;

    return riFlags;
}
// ----- Ray Intersection with Object Bounding Box : End -----

// 3D GLOW TUTORIAL by alro : https://www.shadertoy.com/view/7stGWj
float getGlow(float dist, float radius, float intensity)
{
    return pow(radius / max(abs(dist), 1e-6), intensity);
}

vec3 standardMaterial(vec3 base, vec3 shadow, float fresnelMult, float diffuse, float fresnel, float shadowMult) {
    return mix(shadow, base, diffuse) * shadowMult + base * fresnel * fresnelMult;
}

vec3 calcColor(int matId, vec3 p, vec3 normal, float diffuse, float fresnel, bool insidePortal)
{
    vec3 base = vec3(0.0);
    vec3 shadow = vec3(0.0);
    float fresnelMult = 1.0;
    float shadowMult = 1.0;

    vec3 FinalColor = vec3(0.0);

    switch (matId)
    {
        case MAT_GIRL_SKIN:
        case MAT_GIRL_FACE:
            base = vec3(1.0, 0.58, 0.4);
            shadow = vec3(0.78, 0.46, 0.30);
            fresnelMult = 1.2;
            break;

        case MAT_GIRL_BLONDE:
            //base = vec3(0.780, 0.450, 0.080);
            //shadow = vec3(0.680, 0.380, 0.060);
            base = vec3(0.13, 0.05, 0.01);
            shadow = base * 0.5;
            fresnelMult = 3.0;
            break;

        case MAT_GIRL_BOOTS:
            base = vec3(0.02, 0.02, 0.03);
            shadow = vec3(0.01, 0.01, 0.02);
            fresnelMult = 0.3;
            break;

        case MAT_LEAVES:
        case MAT_TREES:
            base = vec3(0.0882, 0.447, 0.04);
            shadow = vec3(0.00582, 0.247, 0.02);
            fresnelMult = 2.5;
            shadowMult = 0.7;
            break;

        case MAT_STEM:
            base = vec3(0.05, 0.25, 0.05);
            shadow = vec3(0.05, 0.15, 0.05);
            fresnelMult = 2.5;
            shadowMult = 0.7;
            break;

        case MAT_GRASS:
            base = vec3(0.0882, 0.247, 0.04);
            shadow = vec3(0.00582, 0.147, 0.02);
            fresnelMult = 1.5;
            break;

        case MAT_MUSHROOM_STEM:
        case MAT_BUNNY:
            base = vec3(0.95, 0.95, 0.9);
            shadow = vec3(0.85, 0.85, 0.8);
            fresnelMult = 2.5;
            break;

        case MAT_SMALL_FLOWER_PISTIL:
            base = vec3(0.780, 0.450, 0.080);
            shadow = vec3(0.680, 0.380, 0.060);
            fresnelMult = 2.5;
            break;

        case MAT_FLOWER_FACE:
            base = vec3(1.00, 0.80, 0.15);
            shadow = vec3(1.0, 0.6, 0.1);
            fresnelMult = 2.5;
            break;

        case MAT_CASTLE_WHITE:
        case MAT_CASTLE_FACADE:
            base = vec3(1.0, 1.0, 1.0);
            shadow = vec3(0.5, 0.8, 0.9);
            fresnelMult = 0.5;
            break;

        case MAT_CASTLE_ROOF:
            base = COLOR_CASTLE_ROOF;
            shadow = base * 0.7;
            fresnelMult = 0.5;
            break;

        case MAT_GROUND:
            base = vec3(0.28, 0.15, 0.05);
            shadow = base * 0.5;
            FinalColor = mix(shadow, base, mix(0.3, 1.0, diffuse));
            return FinalColor + base * fresnel * 0.8;

        case MAT_CLOUD:
            base = vec3(1.0, 1.0, 1.0);
            shadow = vec3(0.18, 0.70, 0.87);
            FinalColor = mix(shadow, base, mix(0.3, 1.0, diffuse));
            return FinalColor + base * fresnel * 0.8;

        case MAT_GIRL_DRESS:
            vec3 pattern = paintGirlDress(p, normal, 50.0);
            base = vec3(0.08, 0.18, 0.42) + pattern;
            shadow = vec3(0.03, 0.09, 0.22) + pattern;
            fresnelMult = 0.4;
            break;


        case MAT_MUSHROOM_CAP1:
            paintMushroomCap1(p, normal, base, shadow);
            FinalColor = mix(shadow, base, diffuse);
            return FinalColor + vec3(0.8, 0.5, 0.5) * fresnel * 2.5;


        case MAT_MUSHROOM_CAP2:
            paintMushroomCap2(p, normal, base, shadow);
            FinalColor = mix(shadow, base, diffuse);
            return FinalColor + vec3(0.8, 0.5, 0.5) * fresnel * 2.5;

        // case MAT_MUSHROOM_CAP:
        //     paintMushroomCap(p, normal, base, shadow);
        //     FinalColor = mix(shadow, base, diffuse);
        //     return FinalColor + vec3(0.8, 0.5, 0.5) * fresnel * 2.5;

        case MAT_BIFROST:
            {
                vec3 bifrost = getBifrostColor(p);
                FinalColor = bifrost + bifrost * fresnel * (insidePortal ? 2.2 : 0.8);
                return FinalColor + vec3(0.5, 0.7, 1.0) * pow(fresnel, 0.5) * (insidePortal ? 0.1 : 0.4);
            }

        default:
            return vec3(0.1, 0.1, 0.1) * diffuse;
    }

    FinalColor = standardMaterial(base, shadow, fresnelMult, diffuse, fresnel, shadowMult);

    switch(matId)
    {
        case MAT_GIRL_FACE:
            paintFace(p, FinalColor);
            break;
        case MAT_FLOWER_FACE:
            paintFlowerFace(p, FinalColor);
            break;
        case MAT_BUNNY:
            paintBunny(p, FinalColor);
            break;
        case MAT_CASTLE_FACADE:
            paintCastleFacade(p, FinalColor);
            break;
    }

    return FinalColor;
}

const vec3 SUN_DIR_PORTAL = normalize(vec3(-1.5, 0.15, 0.2));

vec3 getSkyColor(vec3 dir, bool insidePortal)
{
    if (!insidePortal) {
        float t = smoothstep(0.1,0.6,0.5*(dir.y+1.0));
        return mix(vec3(0.4,0.4,0.2), vec3(0.4,0.6,1.0), t);
    } else {
        float up = dir.y;
        float skyDot = up*0.5 + 0.5;
        
        float sunDot = dot(dir, SUN_DIR_PORTAL);
        float sunProximity = (sunDot + 1.0) * 0.5;
        
        vec3 warm = mix(vec3(1.0,0.35,0.25), vec3(1.0,0.6,0.7), pow(skyDot,0.1));
        
        vec3 cool = mix(vec3(0.2,0.2,0.4), vec3(0.35,0.25,0.7), pow(skyDot,0.5));
        
        float blend = smoothstep(0.1, 0.9, 1.0 - sunProximity);
        vec3 sky = mix(warm, cool, blend);
        
        float sunGlow = max(sunDot, 0.0);
        sky += vec3(1.0,0.48,0.35) * pow(sunGlow, 10.0) * 2.5;
        
        return sky;
    }
}

//--------------------------------------
// RAYMARCHING 
// https://iquilezles.org/articles/rmshadows
//--------------------------------------
float calcSoftshadow( in vec3 ro, in vec3 rd, in float tmin, in float tmax, in bool inside )
{
    uint riFlags = getRayIntersectionFlags(ro, rd, tmax);
    float res = 1.0;
    float t = tmin;
    for( int i=ZERO; i<60; i++ )
    {
        float h = map( ro + rd*t , inside, riFlags).x;
        if (h < 0.0001) return 0.0;
        float s = clamp(30.*h/t,0.0,1.0);
        res = min( res, s*s*(3.0-2.0*s) );
        t += clamp(h, 0.001, 0.025);
        if( res<0.005 || t>tmax ) break;
    }
    return clamp( res, 0.0, 1.0 );
}

// https://iquilezles.org/articles/normalsSDF
vec3 calcNormal( in vec3 p, in bool inside )
{
    // inspired by tdhooper and klems - a way to prevent the compiler from inlining map() 4 times
    vec3 n = vec3(0.0);
    for( int i=ZERO; i<4; i++ )
    {
        vec3 e = 0.5773*(2.0*vec3((((i+3)>>1)&1),((i>>1)&1),(i&1))-1.0);
        n += e*map(p+0.0005*e, inside, 0xFFFu).x;
    }
    return normalize(n);
}

float calcAO( in vec3 p, in vec3 nor, in bool inside )
{
    float occ = 0.0;
    float sca = 1.0;
    for( int i=ZERO; i<5; i++ )
    {
        float hr = 0.001 + 0.003 * float(i)/4.0;
        vec3 aopos =  nor * hr + p;
        float dd = map( aopos , inside, 0xFFFu ).x;
        occ += -(dd-hr)*sca;
        sca *= 0.75;
    }
    return clamp( 1.0 - 2.5*occ, 0.0, 1.0 ) * (0.5+0.5*nor.y);
}

mat3 setCamera( in vec3 ro, in vec3 ta, float cr )
{
    vec3 cw = normalize(ta-ro);
    vec3 cp = vec3(sin(cr), cos(cr),0.0);
    vec3 cu = normalize( cross(cw,cp) );
    vec3 cv =          ( cross(cu,cw) );
    return mat3( cu, cv, cw );
}

vec4 castRay(vec3 ro, vec3 rd, float time, inout float glow)
{
    float tmin = 3.0, tmax = 8.0, gt = 0.4; vec2 tb;
    bool inside = false;
    float portalDist = portal_intersect(ro, rd);
    glow = 0.0;
    
    if (rayIntersectsBox(ro,rd,vec3(0,.47,1.),vec3(1.31,.72, 2.35), tmax, tb))
    {
        tmin = max(tb.x, tmin);
        tmax = min(tb.y, tmax);
        
        float t = tmin;
        
        uint riFlags = getRayIntersectionFlags(ro, rd, tmax);
        
        for (int i = ZERO; i < 256; i++)
        {
            if (t > portalDist && portalDist < 1e5)
            {
                inside = !inside;
                portalDist = 1e5;
            }
        
            vec3 p = ro + rd * t;
            vec2 h = map(p, inside, riFlags);
        
            float distToTorus = sdPortalTorus(p);
            if (distToTorus < gt) {
                glow += getGlow(distToTorus, 0.001, 0.55) * smoothstep(1.0, 0.0, distToTorus / gt);
            }
            
            if (distToTorus < h.x)
            {
                h.x = distToTorus;
                h.y = float(MAT_GLOW);
            }
            float distToScene = h.x;
        
            if (abs(distToScene) < 1e-4 * t)
                return vec4(t, distToScene, h.y, inside ? 1.0 : 0.0);
        
            t += min(distToScene * 0.5, 0.12);
            
            if (t > tmax) break;
        }
    }
    
    return vec4(tmax, 1e10, 0.0, inside ? 1.0 : 0.0);
}

vec3 render(in vec3 ro, in vec3 rd, in float t)
{
    float glow = 0.0;
    vec4 res = castRay(ro, rd, t, glow);
    bool insidePortal = res.w > 0.5;
    
    vec3 finalColor = getSkyColor(rd, insidePortal);
    vec3 glowColor = vec3(0.2,0.5,1.0);
    float glowFactor = .1;
    
    if(int(res.z) == MAT_GLOW)
    {
        finalColor = vec3(1);
    }
    else if(res.y < 0.002)
    {
        vec3 lightDir = normalize( insidePortal
            ? SUN_DIR_PORTAL
            : vec3(-0.5,1.1,-0.6) );
        float lightIntensity = insidePortal ? 6.0 : 12.0;
        
        vec3 p = ro + rd * res.x;
        vec3 normal = calcNormal(p, insidePortal);
        float ao = calcAO(p, normal, insidePortal);
        float shadow = calcSoftshadow(p, lightDir, 0.0005, 12., insidePortal);
        float NdL = clamp(dot(normal, lightDir),0.0,1.0);
        float fresnel= pow(clamp(1.0+dot(normal,rd),0.0,1.0),2.4);
        float diffuse= shadow * NdL * lightIntensity;
        
        vec3 surfaceColor = calcColor(int(res.z), p, normal, diffuse, fresnel, insidePortal);
        surfaceColor *= mix(0.22,1.0,ao);
        surfaceColor = surfaceColor*0.4 + 0.6*surfaceColor*getSkyColor(normal,insidePortal);
        
        finalColor = surfaceColor;
        
        if(insidePortal)
            finalColor = mix(finalColor, vec3(0.9, 0.65, 0.7), clamp(1.0 - exp(-.01 * res.x), 0.0, 0.95));
    }
    
    finalColor += glowColor * glow * glowFactor;
    
    return finalColor;
}

void main()
{
    vec2 mo = iMouse.xy / iResolution.xy;
    float time = iTime;

    const float ORBIT_RADIUS   = 4.6; 
    const float HEIGHT_MIN     = 0.7;
    const float HEIGHT_RANGE   = 3.0;
    const float MAX_MOUSE_YAW_RAD = radians(75.0);
    const float MAX_TIME_YAW_RAD  = radians(40.0);

    bool mouseActive = iMouse.z > 0.0;
    float autoYaw = sin(time * 0.25) * MAX_TIME_YAW_RAD;
    float mouseYawInput = clamp((mo.x - 0.5) * 2.0, -1.0, 1.0);
    float mouseYaw = mouseYawInput * MAX_MOUSE_YAW_RAD;
    float yaw = mouseActive ? mouseYaw : autoYaw;

    float camHeight = HEIGHT_MIN + HEIGHT_RANGE * mo.y;
    vec3 ro = vec3(
        sin(yaw) * ORBIT_RADIUS,
        camHeight,
        -cos(yaw) * ORBIT_RADIUS
    );

    vec3 ta = vec3(0.0, 0.35, 0.0);

    mat3 ca = setCamera(ro, ta, 0.0);

    vec3 tot = vec3(0.0);

#if AA>1
    for( int m=ZERO; m<AA; m++ )
    for( int n=ZERO; n<AA; n++ )
    {
        vec2 o = vec2(float(m),float(n)) / float(AA) - 0.5;
        vec2 p = (-iResolution.xy + 2.0*(fragCoord+o)) / iResolution.y;
#else
        vec2 p = (-iResolution.xy + 2.0*fragCoord) / iResolution.y;
#endif

        const float fl = 6.0;

        vec3 rd = ca * normalize(vec3(p, fl));

        float t = time * 0.5;
        vec3 col = render(ro, rd, t); 

        col = pow(col, vec3(0.4545));
        col = mix(col, smoothstep(0.0, 1.0, col), 0.5);

        tot += col;

#if AA>1
    }
    tot /= float(AA*AA);
#endif

    fragColor = vec4(tot, 1.0);
}
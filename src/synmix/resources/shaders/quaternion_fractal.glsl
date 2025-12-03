#version 330

in vec2 fragCoord;
out vec4 fragColor;

uniform vec3 iResolution;
uniform float iTime;

// Controllable parameters
uniform float shellIntensity;
uniform float rotationFactor;
uniform float colorVariation;
uniform float raycastSteps;
uniform float cameraZoom0;
uniform float cameraZoom1;
uniform float zoomFreq;
uniform float detailLevel;
uniform float mandelbrotScale0;
uniform float mandelbrotScale1;
uniform float colorIntensity;
uniform float initSc;

#define rot(x) mat2(cos(x+vec4(0,11,33,0)))

//Rodrigues-Euler axis angle rotation
#define ROT(p,axis,t) mix(axis*dot(p,axis),p,cos(t))+sin(t)*cross(p,axis)

#define st(x)  sin(iTime/x)
//formula for creating colors
#define H(h,sn2)  (  cos(  h*h/(3.+(2.+1.*abs(st(1.5)))*sn2) + (1.+4.*sn2)*vec3(2.5*sn2*st(1.2),1.+2.*sn2,4)   )*.9 + .4 )

//formula for mapping scale factor 
#define M(c)  log(c)

#define R iResolution

//polar repeat by fabriceneyret2
vec2 polarRep(vec2 U, float n) {
    n = 6.283/n;
    float a = atan(U.y, U.x),
          r = length(U);
    a = mod(a+n/2.,n) - n/2.;
    U = r * vec2(cos(a), sin(a));
    return .5* ( U+U - vec2(1,0) );
}

void mainImage( out vec4 O, vec2 U) {
  
    O = vec4(0);
    
    vec3 c=vec3(0);
    // Apply zoom to UV coordinates for proper field-of-view control
    float cameraZoom = mix(cameraZoom0, cameraZoom1, 0.5 + 0.5 * sin(iTime * zoomFreq));
    vec2 uv = (U-.5*R.xy) / cameraZoom;
    vec4 rd = normalize( vec4(uv, .8*R.y, R.y))*2000.;
    
    float sc,dotp,totdist=0., t1=.95, tt=iTime;
    float t=0.;
 
    float sn = mod(iTime,20.)<12. ? 0. : 1.;
    float sn2 = mod(iTime,40.)<20. ? 0. : 1.;
    
    for (float i=0.; i<raycastSteps; i++) {
        
        vec4 p = vec4( rd*totdist);
        
        float shell =  length(p) - .1*sn2*shellIntensity;
        p.z += -sn2*2. + (1.-sn)*-18. +sn*-10. + mod( (1.-sn)*tt*3.,40.);
        
        p.xz *= rot( 3.14/2. + sn*tt*rotationFactor );

        p.yzw = p.xyz; 
  
     
        sc = initSc;

        float rotsign = p.x > 0. ? 1. : -1.;
        p.zw *= rot( (tt/3. + sin(tt/2.) )*rotsign);
        
        p.wz = polarRep(p.wz,6.);
   
        vec4 w = p;
     
        for (float j=0.; j<7.+sn2; j++) {
          
            p = abs(p-.3*sn2)*.7;
                        
            dotp = min(max(1./dot(w,w),.1-.05*sn2*(2.-shellIntensity)),1e4*(1.-sn2)+7.*sn2);
            
            sc *= dotp ; 
            
            p = p * dotp  - .9*vec4(.5-.4*sn2,.5,.3-.1*sn2,.3);
            
            w = vec4(0);
            //quaternionic mandelbrot iterations
            float mandelbrotScale = mix(mandelbrotScale0, mandelbrotScale1, 0.5 + 0.5 * sin(iTime * zoomFreq));
            for (float k=0.; k<4.-2.*sn2;  k++) {
                w =
                    vec4( w.x*w.x-w.y*w.y-w.z*w.z-w.w*w.w,
                       2.*w.x*w.y,
                       2.*w.x*w.z,
                       2.*w.x*w.w ) - mandelbrotScale*p*detailLevel;
                                  
            }
        }
         
        float dist = max(-shell,abs( length(p.zw) -.1)/sc) * (1. + shellIntensity);
        float stepsize = dist/200. + 8e-6;     
        totdist += stepsize;
        
        //accumulate color, fading with distance and iteration count
        c +=
             .6e-1* colorIntensity *
             mix( vec3(1), H(M(sc)*colorVariation,sn2),.9)  * exp(-i*i*stepsize*max(1e1,sn2*2e1));
    }
    
    c = 1. - exp(-c*c);
    O = ( vec4(c,0) );
               
}

void main()
{
    mainImage(fragColor, fragCoord);
}

#version 330

in vec2 fragCoord;
out vec4 fragColor;

uniform vec3 iResolution;
uniform float iTime;

// Controllable parameters
uniform float strength;
uniform float fieldScale;
uniform float colorIntensity;
uniform float starBrightness;
uniform float animationPhase;
uniform float pulseBPM;
uniform float fieldOffsetZ;
uniform float animationAmplitude;
uniform float starPower;

// CBS Parallax scrolling fractal galaxy
// Inspired by JoshP's Simplicity shader

float field(in vec3 p, float s) {
	// Convert BPM to Hz (beats per second) and create pulsing effect
	float pulseFreq = pulseBPM / 60.0;
	float pulse = sin(iTime * pulseFreq * 6.283185);
	float str = strength + strength * 0.3 * pulse;
	float accum = s/4.;
	float prev = 0.;
	float tw = 0.;
	for (int i = 0; i < 26; ++i) {
		float mag = dot(p, p);
		p = abs(p) / mag + vec3(-.5, -.4, fieldOffsetZ);
		float w = exp(-float(i) / 7.);
		accum += w * exp(-str * pow(abs(mag - prev), 2.2));
		tw += w;
		prev = mag;
	}
	return max(0., 5. * accum / tw - .7);
}

// Less iterations for second layer
float field2(in vec3 p, float s) {
	// Convert BPM to Hz (beats per second) and create pulsing effect
	float pulseFreq = pulseBPM / 60.0;
	float pulse = sin(iTime * pulseFreq * 6.283185);
	float str = strength + strength * 0.3 * pulse;
	float accum = s/4.;
	float prev = 0.;
	float tw = 0.;
	for (int i = 0; i < 18; ++i) {
		float mag = dot(p, p);
		p = abs(p) / mag + vec3(-.5, -.4, fieldOffsetZ);
		float w = exp(-float(i) / 7.);
		accum += w * exp(-str * pow(abs(mag - prev), 2.2));
		tw += w;
		prev = mag;
	}
	return max(0., 5. * accum / tw - .7);
}

vec3 nrand3( vec2 co )
{
	vec3 a = fract( cos( co.x*7.3e-3 + co.y )*vec3(1.3e5, 4.7e5, 2.9e5) );
	vec3 b = fract( sin( co.x*0.3e-3 + co.y )*vec3(8.1e5, 1.0e5, 0.1e5) );
	vec3 c = mix(a, b, 0.5);
	return c;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
    vec2 uv = 2. * fragCoord.xy / iResolution.xy - 1.;
	vec2 uvs = uv * iResolution.xy / max(iResolution.x, iResolution.y);
	float animTime = iTime * animationPhase;
	vec3 p = vec3(uvs / fieldScale, 0) + vec3(1., -1.3, 0.);
	p += animationAmplitude * vec3(sin(animTime / 16.), sin(animTime / 12.),  sin(animTime / 128.));
	
	float freqs[4];
	freqs[0] = 0.5;
	freqs[1] = 0.6;
	freqs[2] = 0.7;
	freqs[3] = 0.8;

	float t = field(p, freqs[2]);
	float v = (1. - exp((abs(uv.x) - 1.) * 6.)) * (1. - exp((abs(uv.y) - 1.) * 6.));
	
    // Second Layer
	vec3 p2 = vec3(uvs / (fieldScale + sin(animTime*0.11)*0.2 + 0.2 + sin(animTime*0.15)*0.3 + 0.4), 1.5) + vec3(2., -1.3, -1.);
	p2 += 0.25 * vec3(sin(animTime / 16.), sin(animTime / 12.),  sin(animTime / 128.));
	float t2 = field2(p2, freqs[3]);
	vec4 c2 = mix(.4, 1., v) * vec4(1.3 * t2 * t2 * t2, 1.8 * t2 * t2, t2 * freqs[0], t2);
	
	// Stars
	vec2 seed = p.xy * 2.0;	
	seed = floor(seed * iResolution.x);
	vec3 rnd = nrand3( seed );
	vec4 starcolor = vec4(pow(rnd.y, starPower));
	
	// Second Layer stars
	vec2 seed2 = p2.xy * 2.0;
	seed2 = floor(seed2 * iResolution.x);
	vec3 rnd2 = nrand3( seed2 );
	starcolor += vec4(pow(rnd2.y, starPower));
	
	fragColor = colorIntensity * (mix(freqs[3] - .3, 1., v) * vec4(1.5 * freqs[2] * t * t * t, 1.2 * freqs[1] * t * t, freqs[3] * t, 1.0) + c2 + starcolor * starBrightness);
}

void main()
{
    mainImage(fragColor, fragCoord);
}

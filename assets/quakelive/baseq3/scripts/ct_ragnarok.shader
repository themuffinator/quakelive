//-----------------------------------------------------------------
//-----Tom 'Phantazm11' Perryman
//-----www.phantazm11.com
//-----phantazm11(at)gmail[dot]com
//-----08.11.2011
//-----------------------------------------------------------------

textures/ct_ragnarok/ct_ragnarok_floor_003
{

	{
		map textures/ct_ragnarok/ct_ragnarok_env.tga
		tcgen environment
		rgbgen wave sin .35 0 0 0
	}


	{
		map textures/ct_ragnarok/ct_ragnarok_floor_003.tga
		blendFunc GL_ZERO GL_SRC_ALPHA
		tcmod scale .9 .9
		rgbgen identity	
	}

	{
		map textures/ct_ragnarok/ct_ragnarok_floor_003.tga
		blendFunc GL_ONE GL_SRC_ALPHA
		rgbgen identity	
	}


	{
		map $lightmap
        	blendfunc gl_dst_color gl_zero
		rgbgen identity 
	}
}

textures/ct_ragnarok/ct_ragnarok_floor_003_snow
{

	{
		map textures/ct_ragnarok/ct_ragnarok_env.tga
		tcgen environment
		rgbgen wave sin .35 0 0 0
	}


	{
		map textures/ct_ragnarok/ct_ragnarok_floor_003_snow.tga
		blendFunc GL_ZERO GL_SRC_ALPHA
		tcmod scale .9 .9
		rgbgen identity	
	}

	{
		map textures/ct_ragnarok/ct_ragnarok_floor_003_snow.tga
		blendFunc GL_ONE GL_SRC_ALPHA
		rgbgen identity	
	}


	{
		map $lightmap
        	blendfunc gl_dst_color gl_zero
		rgbgen identity 
	}
}

textures/ct_ragnarok/floor_02b_snow_wet
{
	qer_editorimage textures/ct_ragnarok/floor_02b_snow.tga

	{
		map textures/ct_ragnarok/ct_ragnarok_env.tga
		tcgen environment
		rgbgen wave sin .35 0 0 0
	}


	{
		map textures/ct_ragnarok/floor_02b_snow.tga
		blendFunc GL_ZERO GL_SRC_ALPHA
		tcmod scale .9 .9
		rgbgen identity	
	}

	{
		map textures/ct_ragnarok/floor_02b_snow.tga
		blendFunc GL_ONE GL_SRC_ALPHA
		rgbgen identity	
	}


	{
		map $lightmap
        	blendfunc gl_dst_color gl_zero
		rgbgen identity 
	}
}

textures/ct_ragnarok/ct_ragnarok_wood_001_wet
{

	{
		map textures/ct_ragnarok/ct_ragnarok_env_wood.tga
		tcgen environment
		rgbgen wave sin .12 .2 0 0
	}


	{
		map textures/ct_ragnarok/ct_ragnarok_wood_001_wet.tga
		blendFunc GL_ZERO GL_SRC_ALPHA
		tcmod scale .2 .2
		rgbgen identity	
	}

	{
		map textures/ct_ragnarok/ct_ragnarok_wood_001_wet.tga
		blendFunc GL_ONE GL_SRC_ALPHA
		rgbgen identity	
	}


	{
		map $lightmap
        	blendfunc gl_dst_color gl_zero
		rgbgen identity 
	}
}


textures/ct_ragnarok/ct_ragnarok_jp_fx
{
	surfaceparm nodamage
	q3map_surfacelight 600
	{
		clampmap textures/ct_ragnarok/ct_ragnarok_jp_fx.tga
		blendFunc GL_ONE GL_ONE
                tcMod rotate 75
	}

}

textures/ct_ragnarok/ct_ragnarok_portal
{
	qer_editorimage textures/ct_ragnarok/ct_ragnarok_portal_3.tga
	qer_trans .5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	nopicmip
	cull disable
	{ 
		clampmap textures/ct_ragnarok/ct_ragnarok_portal_3.tga
		blendFunc Blend
		rgbgen identity
		tcMod rotate 25
	}
	{ 
		clampmap textures/ct_ragnarok/ct_ragnarok_portal_3.tga
		blendFunc Blend
		rgbgen identity
		tcMod rotate 75
		tcMod stretch sin 1.125 .5 .1 .1
	}

	{
		map $lightmap
		blendFunc GL_dst_color GL_zero
		rgbgen identity		
	}
	

}

textures/ct_ragnarok/ct_ragnarok_rings
{
	qer_editorimage textures/ct_ragnarok/ct_ragnarok_rings.tga
	surfaceparm alphashadow
    	surfaceparm trans	
	surfaceparm nonsolid
        surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map textures/ct_ragnarok/ct_ragnarok_rings.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

textures/ct_ragnarok/ct_ragnarok_rain
{
	qer_editorimage textures/ct_ragnarok/ct_ragnarok_rain_editor.tga
        surfaceparm trans	
        surfaceparm nomarks	
        surfaceparm nonsolid
	surfaceparm nolightmap
        qer_trans .5
	cull none
       
	{
		map textures/ct_ragnarok/ct_ragnarok_rain.tga
                tcMod Scroll .1 -4
                tcMod turb .1 .25 0 -.1
                blendFunc GL_ONE GL_ONE
        }
}

textures/ct_ragnarok/ct_ragnarok_sky_001

{
	skyparms - 512 -

	q3map_lightImage textures/ct_ragnarok/ct_ragnarok_sky_001.tga

	q3map_sunExt .77 .91 1 75 80 60 3 16
	q3map_lightmapFilterRadius 0 16		//self other
	q3map_skyLight 108 4

	surfaceparm sky
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nodlight

	nopicmip
	nomipmaps

	qer_editorimage textures/ct_ragnarok/ct_ragnarok_sky_001.tga

	{
		map textures/ct_ragnarok/ct_ragnarok_sky_001.tga
		tcMod scale 8 8
		tcMod scroll .02 .05
		depthWrite
	}


	{
		map textures/ct_ragnarok/ct_ragnarok_sky_001.tga
		blendFunc GL_ONE GL_ONE
		tcMod scale 4 4
		tcMod scroll 0.03 0.05
	}
} 

textures/ct_ragnarok/ct_ragnarok_window_light
{
	surfaceparm nolightmap
	surfaceparm nodlight
	qer_editorimage textures/ct_ragnarok/ct_ragnarok_window_light.tga

	{
		map textures/ct_ragnarok/ct_ragnarok_window_light.tga
	}
} 

textures/ct_ragnarok/tp_metal_fence_grate
{
	surfaceparm alphashadow
	surfaceparm metalsteps
	surfaceparm nomarks
	surfaceparm trans
	cull disable
	nopicmip
	{
		map textures/ct_ragnarok/tp_metal_fence_grate.tga
		rgbGen identity
		depthWrite
		alphaFunc GE128
	}
	{
		map $lightmap 
		blendfunc filter
		rgbGen identity
		tcGen lightmap 
		depthFunc equal
	}
}

textures/ct_ragnarok/tp_spiderweb_001
{
	qer_editorimage textures/ct_ragnarok/tp_spiderweb_001.tga
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nonsolid
	qer_trans 0.5
	cull none
	tessSize 32
        deformVertexes wave 194 sin 0 3 0 .4
        deformVertexes normal .3 .2
	
	
	{
		map textures/ct_ragnarok/tp_spiderweb_001.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}
}

textures/ct_ragnarok/tp_spiderweb_004
{
	qer_editorimage textures/ct_ragnarok/tp_spiderweb_004.tga
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nonsolid
	qer_trans 0.5
	cull none
	tessSize 32
        deformVertexes wave 194 sin 0 3 0 .4
        deformVertexes normal .3 .2
	
	{
		map textures/ct_ragnarok/tp_spiderweb_004.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}
}

textures/ct_ragnarok/tp_spiderweb_005
{
	qer_editorimage textures/ct_ragnarok/tp_spiderweb_005.tga
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nonsolid
	qer_trans 0.5
	cull none
	tessSize 32
        deformVertexes wave 194 sin 0 3 0 .4
        deformVertexes normal .3 .2
	
	{
		map textures/ct_ragnarok/tp_spiderweb_005.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}
}

textures/ct_ragnarok/ct_ragnarok_torchlight
{
	qer_editorimage textures/sfx/flame1.tga
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm trans
	cull none
	q3map_surfacelight 800
	

	{
		animMap 10 textures/sfx/flame1.tga textures/sfx/flame2.tga textures/sfx/flame3.tga textures/sfx/flame4.tga textures/sfx/flame5.tga textures/sfx/flame6.tga textures/sfx/flame7.tga textures/sfx/flame8.tga
		blendFunc GL_ONE GL_ONE
		rgbGen wave inverseSawtooth 0 1 0 10
		
	}	
	{
		animMap 10 textures/sfx/flame2.tga textures/sfx/flame3.tga textures/sfx/flame4.tga textures/sfx/flame5.tga textures/sfx/flame6.tga textures/sfx/flame7.tga textures/sfx/flame8.tga textures/sfx/flame1.tga
		blendFunc GL_ONE GL_ONE
		rgbGen wave sawtooth 0 1 0 10
	}	


	{
		map textures/sfx/flameball.tga
		blendFunc GL_ONE GL_ONE
		rgbGen wave sin .6 .2 0 .6	
	}

}

textures/ct_ragnarok/ct_ragnarok_stainedglass_001
{
   qer_editorimage textures/ct_ragnarok/ct_ragnarok_stainedglass_001.tga
	
   surfaceparm lightfilter
   surfaceparm nolightmap

   cull disable

   q3map_lightmapFilterRadius 0 4
   q3map_surfacelight 100
   {
      map textures/ct_ragnarok/ct_ragnarok_stainedglass_001.tga
      blendFunc GL_DST_COLOR GL_ZERO
      rgbGen identity
   }
}


textures/ct_ragnarok/ct_ragnarok_stainedglass_002
{
   qer_editorimage textures/ct_ragnarok/ct_ragnarok_stainedglass_002.tga
	
   surfaceparm lightfilter
   surfaceparm nolightmap

   cull disable

   q3map_lightmapFilterRadius 0 4
   q3map_surfacelight 100
   {
      map textures/ct_ragnarok/ct_ragnarok_stainedglass_002.tga
      blendFunc GL_DST_COLOR GL_ZERO
      rgbGen identity
   }
}

textures/ct_ragnarok/ct_ragnarok_stainedglass_003
{
   qer_editorimage textures/ct_ragnarok/ct_ragnarok_stainedglass_003.tga
	
   surfaceparm lightfilter
   surfaceparm nolightmap

   cull disable

   q3map_lightmapFilterRadius 0 4
   q3map_surfacelight 100
   {
      map textures/ct_ragnarok/ct_ragnarok_stainedglass_003.tga
      blendFunc GL_DST_COLOR GL_ZERO
      rgbGen identity
   }
}
textures/ct_ragnarok/ct_ragnarok_stainedglass_004
{
	qer_editorimage textures/ct_ragnarok/ct_ragnarok_stainedglass_002.tga
	q3map_lightimage textures/ct_ragnarok/ct_ragnarok_stainedglass_002.tga
	q3map_surfacelight 200
	q3map_bounceScale 64
        {
		map textures/ct_ragnarok/ct_ragnarok_stainedglass_002.tga
               // blendFunc GL_DST_COLOR GL_ZERO
                rgbGen identity
	}

        {
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}



}

textures/ct_ragnarok/ct_ragnarok_window_002
{
	qer_editorimage textures/ct_ragnarok/ct_ragnarok_window_002.tga
	q3map_lightimage textures/ct_ragnarok/ct_ragnarok_window_002.tga
	q3map_surfacelight 500
        {
		map textures/ct_ragnarok/ct_ragnarok_window_002.tga
               // blendFunc GL_DST_COLOR GL_ZERO
                rgbGen identity
	}

        {
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

//Quad Banner

textures/ct_ragnarok/banner_01
{
        tessSize 64
        deformVertexes wave 194 sin 0 3 0 .4
        deformVertexes normal .3 .2
        surfaceparm nomarks
        cull none

    {
		map textures/ct_ragnarok/banner_01.tga
		rgbGen identity
	}
    {
		map textures/ct_ragnarok/banner_01.tga
                blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}
    {
		map $lightmap
                blendFunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
    {

        	map textures/sfx/shadow.tga
                tcGen environment 
                //blendFunc GL_ONE GL_ONE            
                blendFunc GL_DST_COLOR GL_ZERO
               rgbGen identity
	}
}

//RA Banner

textures/ct_ragnarok/banner_02
{
        tessSize 64
        deformVertexes wave 194 sin 0 3 0 .4
        deformVertexes normal .3 .2
        surfaceparm nomarks
        cull none

    {
		map textures/ct_ragnarok/banner_02.tga
		rgbGen identity
	}
    {
		map textures/ct_ragnarok/banner_02.tga
                blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}
    {
		map $lightmap
                blendFunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
    {
        	map textures/sfx/shadow.tga
                tcGen environment 
                //blendFunc GL_ONE GL_ONE            
                blendFunc GL_DST_COLOR GL_ZERO
               rgbGen identity
	}
}

// Ring Light

textures/ct_ragnarok/lamp_01
{
	surfaceparm nomarks
	qer_editorimage textures/ct_ragnarok/lamp_01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ragnarok/lamp_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ragnarok/lamp_01_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_ragnarok/lamp_02
{
	surfaceparm nomarks
	qer_editorimage textures/ct_ragnarok/lamp_02.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ragnarok/lamp_02.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ragnarok/lamp_02_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_ragnarok/lamp_03
{
	surfaceparm nomarks
	qer_editorimage textures/ct_ragnarok/lamp_03.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ragnarok/lamp_03.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_ragnarok/lamp_03_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_ragnarok/grate_01
{
	surfaceparm alphashadow
	surfaceparm metalsteps
	surfaceparm nomarks
	surfaceparm trans
	cull disable
	nopicmip
	{
		map textures/ct_ragnarok/grate_01.tga
		rgbGen identity
		depthWrite
		alphaFunc GE128
	}
	{
		map $lightmap 
		blendfunc filter
		rgbGen identity
		tcGen lightmap 
		depthFunc equal
	}
}

textures/ct_ragnarok/rock_03
{
	qer_editorimage textures/ct_ragnarok/rock_03.tga
	
	q3map_nonplanar
	q3map_shadeAngle 90
	
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ragnarok/rock_03.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/ct_ragnarok/rock_03_snow
{
	qer_editorimage textures/ct_ragnarok/rock_03_snow.tga
	
	q3map_nonplanar
	q3map_shadeAngle 90
	
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ragnarok/rock_03_snow.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/ct_ragnarok/sky
{
	qer_editorimage textures/skies/env/devilish_rt.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	surfaceparm sky
	q3map_lightImage textures/skies/meth_clouds_blue.tga
	skyparms textures/skies/env/devilish 512 -
	
	q3map_sunExt 0.569696 0.653742 0.71902 90 225 80 3 16
	q3map_lightmapFilterRadius 0 12		//self other
	q3map_skyLight 100 3
	
	nopicmip
	nomipmaps
	{
		map textures/skies/meth_clouds3.tga
		blendfunc filter
		tcMod scale 3 2
		tcMod scroll 0.02 0.04
	}
	{
		map textures/skies/devilish_dimclouds.tga
		blendfunc add
		tcMod scale 5 5
		tcMod scroll 0.02 0.02
	}
}

textures/ct_ragnarok/jp_swirl
{
	q3map_surfacelight	300
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	qer_editorimage textures/sfx/swirl_b1.tga
	{
		clampmap textures/sfx/swirl_b1.tga
		blendfunc add
		tcmod rotate -188
	}
	{
		clampmap textures/sfx/swirl_b2.tga
		blendfunc add
		tcmod rotate 333
	}
}

textures/ct_ragnarok/lavahell_large
{
	qer_editorimage textures/ct_ragnarok/lavahell_large.tga
	q3map_globaltexture
	surfaceparm trans
	surfaceparm noimpact
	surfaceparm lava
	surfaceparm nolightmap
	q3map_surfacelight 1000
	cull disable
	tesssize 128
	cull disable
	// deformVertexes wave 100 sin 3 2 .1 0.1
	{
		map textures/ct_ragnarok/lavahell_large.tga
		tcMod turb 0 .1 0 .1
	}
}

textures/ct_ragnarok/lavahell_large_500
{
	qer_editorimage textures/ct_ragnarok/lavahell_large.tga
	q3map_globaltexture
	surfaceparm trans
	surfaceparm noimpact
	surfaceparm lava
	surfaceparm nolightmap
	q3map_surfacelight 500
	cull disable
	q3map_lightsubdivide 64
	tesssize 128
	cull disable
	// deformVertexes wave 100 sin 3 2 .1 0.1
	{
		map textures/ct_ragnarok/lavahell_large.tga
		tcMod turb 0 .1 0 .1
	}
}

//LARGE WINDOWS

textures/ct_ragnarok/window_large
{
   qer_editorimage textures/ct_ragnarok/window_large.tga
   surfaceparm lightfilter
   //surfaceparm nolightmap
   cull disable
   q3map_lightmapFilterRadius 0 4
   q3map_surfacelight 100
   	{
		map $lightmap
		rgbGen identity
	} 
    {
     	map textures/ct_ragnarok/window_large.tga
     	blendFunc GL_DST_COLOR GL_ZERO
      	rgbGen identity
    }
    {
		map textures/ct_ragnarok/window_large_blend.tga
		blendFunc add
    }
}

textures/ct_ragnarok/window_large_2
{
   qer_editorimage textures/ct_ragnarok/window_large_2.tga
   surfaceparm lightfilter
   //surfaceparm nolightmap
   cull disable
   q3map_lightmapFilterRadius 0 4
   q3map_surfacelight 80
   	{
		map $lightmap
		rgbGen identity
	}
    {
      	map textures/ct_ragnarok/window_large_2.tga
      	blendFunc GL_DST_COLOR GL_ZERO
      	rgbGen identity
    }
    {
		map textures/ct_ragnarok/window_large_2_blend.tga
 		blendFunc GL_ONE GL_ONE
 	}
}

// CHAIN
// 256*512 with alpha channel

textures/ct_ragnarok/chain_01
{
	surfaceparm nomarks
    cull disable
	nopicmip
    //deformVertexes autoSprite2
    {
		map textures/ct_ragnarok/chain_01.tga
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

// LAVA ROCK
// 256*512 with alpha channel

textures/ct_ragnarok/lava_cross
{
     cull disable
    {
		map textures/ct_ragnarok/lava_cross.tga
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

//ACCEL PAD
textures/ct_ragnarok/valknut
{
	q3map_surfacelight	300
	surfaceparm trans
	qer_trans 0.5
	surfaceparm nomarks
	surfaceparm nonsolid
	//surfaceparm nolightmap
	cull none
	qer_editorimage textures/ct_ragnarok/valknut.jpg
	{
		clampmap textures/ct_ragnarok/valknut.jpg
		blendfunc add
		//tcmod scroll 0 0.5 
		rgbGen wave inversesawtooth -0.5 1.5 0 .5
	}
	{
		clampmap textures/ct_ragnarok/valknut_blend.jpg
		tcMod stretch sin 1.0 .1 0 .5
		rgbGen wave square .5 .5 .25 1
		blendFunc add
	}
}

textures/ct_ragnarok/accelpad_beam
{
	qer_editorimage textures/sfx/beam_blue4.tga
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	qer_trans .6
	cull none
	nopicmip
	{
		map textures/sfx/beam_blue4.tga
		tcMod Scroll .3 0
		//tcMod stretch sawtooth -0.5 1.5 0 .5
		blendfunc add
	} 
}

//TELEPORTER

textures/ct_ragnarok/tp_dragon_01
{
	qer_editorimage textures/ct_ragnarok/tp_dragon.jpg
	surfaceparm noimpact
	surfaceparm nolightmap
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nodlight
	deformvertexes move 0 0 80 sawtooth 0 1 1 .5
	{
		clampmap textures/ct_ragnarok/tp_dragon.jpg
		rgbGen wave sawtooth 1 -1 1 .5
		blendfunc add
	}
}

textures/ct_ragnarok/tp_dragon_02
{
	qer_editorimage textures/ct_ragnarok/tp_dragon.jpg
	surfaceparm noimpact
	surfaceparm nolightmap
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nodlight
	deformvertexes move 0 0 80 sawtooth 0 1 .66 .5
	{
		clampmap textures/ct_ragnarok/tp_dragon.jpg
		rgbGen wave sawtooth 1 -1 .66 .5
		blendfunc add
	}
}

textures/ct_ragnarok/tp_dragon_03
{
	qer_editorimage textures/ct_ragnarok/tp_dragon.jpg
	surfaceparm noimpact
	surfaceparm nolightmap
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nodlight
	deformvertexes move 0 0 80 sawtooth 0 1 .33 .5
	{
		clampmap textures/ct_ragnarok/tp_dragon.jpg
		rgbGen wave sawtooth 1 -1 .33 .5
		blendfunc add
	}
}

textures/ct_ragnarok/tp_dragon_04
{
	qer_editorimage textures/ct_ragnarok/tp_dragon.jpg
	surfaceparm noimpact
	surfaceparm nolightmap
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nodlight
	deformvertexes move 0 0 80 sawtooth 0 1 0 .5
	{
		clampmap textures/ct_ragnarok/tp_dragon.jpg
		rgbGen wave sawtooth 1 -1 0 .5
		blendfunc add
	}
}

//RA CURSE SYMBOL

textures/ct_ragnarok/frost_curse
{
	qer_editorimage textures/ct_ragnarok/frost_curse_1.jpg
	surfaceparm noimpact
	surfaceparm nolightmap
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nodlight
	{
		map textures/ct_ragnarok/frost_curse_1.jpg
		rgbGen identity
		blendfunc add
		tcmod rotate 10
	}
	{
		map textures/ct_ragnarok/frost_curse_2.jpg
		rgbGen identity
		blendfunc add
		tcmod rotate 60
	}
	{
		map textures/ct_ragnarok/frost_curse_3.jpg
		rgbGen identity
		blendfunc add
		tcmod rotate 45
	}
}

//ICICLES

textures/ct_ragnarok/icicles
{
	qer_editorimage textures/ql/flat.tga
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm nodlight
	surfaceparm nonsolid
	//surfaceparm trans
	//qer_trans 0.5
	cull disable
	polygonOffset
	sort 6
	{
		map textures/ql/flat_2.tga
		blendfunc filter
	}
	{
		map textures/effects/tinfx_eyetoeye.tga
		blendfunc add
		rgbGen identity
		tcGen environment
	}
}

//SNOW DECAL

textures/ct_ragnarok/snow_decal
{
	qer_editorimage textures/ct_ragnarok/snow_decal.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nodlight
	polygonOffset
	sort 6
	{
		map textures/ct_ragnarok/snow_decal.tga
		rgbGen identity
		blendfunc add
	}
}

//ICICLE SPRITE

textures/ct_ragnarok/icicle_sprite
{
	qer_editorimage textures/ct_ragnarok/icicle_sprite.tga
	surfaceparm trans
	cull none
	nopicmip

	{
		map textures/ct_ragnarok/icicle_sprite.tga
		tcMod scale 1 1
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

//NONSOLID RUST

textures/ct_ragnarok/tp_base_rust_02_nonsolid
{
	
	qer_editorimage textures/phantq3dm3/tp_base_rust_02.tga
	surfaceparm nonsolid
	{
		
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/phantq3dm3/tp_base_rust_02.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

//QUAD SYMBOL

textures/ct_ragnarok/gothic_block_large_quad_anim
{
	qer_editorimage textures/ct_ragnarok/gothic_block_large_quad_blend.tga
	surfaceparm nomarks
	surfaceparm trans
	cull none
	{
		
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ragnarok/gothic_block_large_quad_blend.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		clampmap textures/ct_ragnarok/gothic_block_large_quad_blend2.tga
		rgbGen wave sin 1 -1 .8 0.1
		blendfunc add
	}	
	{
		clampmap textures/ct_ragnarok/gothic_block_large_quad_blend3.tga
		rgbGen wave sin 1 -1 .325 0.08
		blendfunc add
	}		
}

textures/ct_ragnarok/gothic_block_large_suit_anim
{
	qer_editorimage textures/ct_ragnarok/gothic_block_large_suit.tga
	surfaceparm nomarks
	surfaceparm trans
	cull none
	{
		
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_ragnarok/gothic_block_large_suit.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		clampmap textures/ct_ragnarok/gothic_block_large_suit_blend1.tga
		rgbGen wave sin 1 -1 .8 0.1
		blendfunc add
	}	
	{
		clampmap textures/ct_ragnarok/gothic_block_large_suit_blend1.tga
		rgbGen wave sin 1 -1 .325 0.08
		blendfunc add
	}		
}

//DOOR TO QUAKE HEAVEN
textures/ct_ragnarok/doortoquakeheaven
{
	qer_editorimage textures/ct_ragnarok/doortoquakeheaven.tga
	surfaceparm nomarks
	surfaceparm trans
	qer_trans 0.5
	surfaceparm nolightmap
	cull none
	{
		map textures/ct_ragnarok/doortoquakeheaven.tga
		blendfunc add
	}		
}

//STAINGLASS CIRCULAR

textures/ct_ragnarok/stainglass_01
{
   qer_editorimage textures/ct_ragnarok/stainglass_01.tga
	
   surfaceparm lightfilter
   surfaceparm nolightmap

   cull disable

   q3map_lightmapFilterRadius 0 4
   q3map_surfacelight 100
   {
      map textures/ct_ragnarok/stainglass_01.tga
      blendFunc GL_DST_COLOR GL_ZERO
      rgbGen identity
   }
	{
		map textures/ct_ragnarok/stainglass_01_blend.tga
		blendfunc add
	}		
  
}

textures/ct_ragnarok/stainglass_01_solid
{
   qer_editorimage textures/ct_ragnarok/stainglass_01.tga
	{
		map $lightmap
		rgbgen identity      
	}
   {
      map textures/ct_ragnarok/stainglass_01.tga
      blendFunc GL_DST_COLOR GL_ZERO
      rgbGen identity
   }
}

//LAVAFALL

textures/ct_ragnarok/lavafall
{
	qer_editorimage textures/ct_ragnarok/lavahell_large.tga
	q3map_globaltexture
	surfaceparm nonsolid
	cull disable
	surfaceparm noimpact
	surfaceparm nomarks
	surfaceparm lava
	surfaceparm nolightmap
	q3map_surfacelight 100
	tesssize 128
	deformvertexes wave 192 sin 0 2 0 .5
	{
		map textures/ct_ragnarok/lavahell_large.tga
		tcmod scroll 0 -.5
		tcMod turb 0 .05 0 .02
	}
}

textures/ct_ragnarok/lavahell_large_lavafall
{
	qer_editorimage textures/ct_ragnarok/lavahell_large.tga
	q3map_globaltexture
	surfaceparm trans
	surfaceparm noimpact
	surfaceparm lava
	surfaceparm nolightmap
	q3map_surfacelight 1000
	cull disable
	tesssize 128
	cull disable
	deformVertexes wave 100 sin 3 2 .1 0.1
	{
		map textures/ct_ragnarok/lavahell_large.tga
		tcMod turb 0 .1 0 .1
	}
}

//LAVA SPRITES

//TELEPORTER SPRITES

textures/ct_ragnarok/lava_sprite_freq08
{
	qer_editorimage textures/ct_1997/tp_flare_01.jpg
	qer_trans .5	
	surfaceparm noimpact
	surfaceparm nolightmap
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nodlight
	deformVertexes autosprite
	deformvertexes move 0 0 80 sawtooth 0 1 1 0.5
	{
		clampmap textures/ct_1997/tp_flare_01.jpg
		rgbGen wave sawtooth 1 -1 1 1
		blendfunc add
	}
}

textures/ct_ragnarok/lava_sprite_freq05
{
	qer_editorimage textures/ct_1997/tp_flare_01.jpg
	qer_trans .5	
	surfaceparm noimpact
	surfaceparm nolightmap
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nodlight
	deformVertexes autosprite
	deformvertexes move 0 0 80 sawtooth 0 1 0.4 0.4
	{
		clampmap textures/ct_1997/tp_flare_01.jpg
		rgbGen wave sawtooth 1 -1 1 1
		blendfunc add
	}
}

textures/ct_ragnarok/lava_sprite_freq07
{
	qer_editorimage textures/ct_1997/tp_flare_01.jpg
	qer_trans .5	
	surfaceparm noimpact
	surfaceparm nolightmap
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nodlight
	deformVertexes autosprite
	deformvertexes move 0 0 80 sawtooth 0 1 0.2 0.2
	{
		clampmap textures/ct_1997/tp_flare_01.jpg
		rgbGen wave sawtooth 1 -1 1 1
		blendfunc add
	}
}

//WOOD FLOOR

textures/ct_ragnarok/infinity_wood_nonsolid
{
	qer_editorimage textures/ct_infinity/floor_03.tga
	surfaceparm	nonsolid
	{
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/ct_infinity/floor_03.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

//BANNERS NEW

textures/ct_ragnarok/ragnarok_banner_blue
{
        tessSize 64
        deformVertexes wave 194 sin 0 3 0 .4
        deformVertexes normal .3 .2
        surfaceparm nomarks
        cull none

    {
		map textures/ct_ragnarok/ragnarok_banner_blue.tga
		rgbGen identity
	}
    {
		map textures/ct_ragnarok/ragnarok_banner_blue.tga
                blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}
    {
		map $lightmap
                blendFunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
    {

        	map textures/sfx/shadow.tga
                tcGen environment 
                //blendFunc GL_ONE GL_ONE            
                blendFunc GL_DST_COLOR GL_ZERO
               rgbGen identity
	}
}

textures/ct_ragnarok/ragnarok_banner_yellow
{
        tessSize 64
        deformVertexes wave 194 sin 0 3 0 .4
        deformVertexes normal .3 .2
        surfaceparm nomarks
        cull none

    {
		map textures/ct_ragnarok/ragnarok_banner_yellow.tga
		rgbGen identity
	}
    {
		map textures/ct_ragnarok/ragnarok_banner_yellow.tga
                blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}
    {
		map $lightmap
                blendFunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
    {

        	map textures/sfx/shadow.tga
                tcGen environment 
                //blendFunc GL_ONE GL_ONE            
                blendFunc GL_DST_COLOR GL_ZERO
               rgbGen identity
	}
}

//ROOFTOP DRAGON HEAD

textures/ct_ragnarok/dragonhead
{
	cull front
	nopicmip
	qer_trans 0.5
	{
		map textures/ct_ragnarok/dragonhead.tga
		rgbGen identity
		depthWrite
		alphaFunc GE128
	}
	{
		map $lightmap 
		blendfunc filter
		rgbGen identity
		tcGen lightmap 
		depthFunc equal
	}
}

//CURSE BANNER

textures/ct_ragnarok/curse_banner
{
	qer_editorimage textures/ct_ragnarok/curse_banner.tga
	surfaceparm nonsolid
    {
		map textures/ct_ragnarok/curse_banner.tga
        rgbGen identity
	}
    {
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/skies/ragnarok_skydark
{
	qer_editorimage textures/skies/sky_dark.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	nopicmip
	q3map_globaltexture
	surfaceparm sky

	q3map_lightmapFilterRadius 0 12		//self other
	q3map_lightsubdivide 256
	q3map_surfacelight 200
	q3map_sunExt 0.922408 0.716442 0.74818 150 70 60 3 16
	skyparms - 256 -
	{
		map textures/skies/sky_dark_2.tga
		tcMod scale 10 10
		tcMod scroll .05 .09
		depthWrite
	}
	{
		map textures/skies/sky_dark.tga
		blendFunc GL_ONE GL_ONE
		tcMod scale 4 4
		tcMod scroll 0.01 0.01
	}
} 





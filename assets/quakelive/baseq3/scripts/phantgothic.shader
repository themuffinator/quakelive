//-----------------------------------------------------------------
//-----Tom 'Phantazm11' Perryman
//-----www.phantazm11.com
//-----phantazm11(at)gmail[dot]com
//-----08.11.2011
//-----------------------------------------------------------------

textures/phantgothic/phantgothic_floor_003
{
	{
		map textures/phantgothic/phantgothic_env.tga
		tcgen environment
		rgbgen wave sin .35 0 0 0
	}
	{
		map textures/phantgothic/phantgothic_floor_003.tga
		blendFunc GL_ZERO GL_SRC_ALPHA
		tcmod scale .9 .9
		rgbgen identity	
	}
	{
		map textures/phantgothic/phantgothic_floor_003.tga
		blendFunc GL_ONE GL_SRC_ALPHA
		rgbgen identity	
	}
	{
		map $lightmap
        	blendfunc gl_dst_color gl_zero
		rgbgen identity 
	}
}

textures/phantgothic/phantgothic_metal_001_nonsolid
{
	qer_editorimage textures/phantgothic/phantgothic_metal_001.tga
	surfaceparm	nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantgothic/phantgothic_metal_001.tga
		blendfunc filter
	}
}

textures/phantgothic/phantgothic_trim_005_nonsolid
{
	qer_editorimage textures/phantgothic/phantgothic_trim_005.tga
	surfaceparm	nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantgothic/phantgothic_trim_005.tga
		blendfunc filter
	}
}

textures/phantgothic/phantgothic_roofslate_001_slick
{
	qer_editorimage textures/phantgothic/phantgothic_roofslate_001.tga
	surfaceparm slick
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantgothic/phantgothic_roofslate_001.tga
		blendfunc filter
	}
}

textures/phantgothic/phantgothic_wood_001
{
	surfaceparm woodsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantgothic/phantgothic_wood_001.tga
		blendFunc filter
	}
}

textures/phantgothic/phantgothic_wood_001_nonsolid
{
	qer_editorimage textures/phantgothic/phantgothic_wood_001.tga
	surfaceparm nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantgothic/phantgothic_wood_001.tga
		blendFunc filter
	}
}

textures/phantgothic/phantgothic_wood_001_wet
{
	surfaceparm woodsteps
	{
		map textures/phantgothic/phantgothic_env_wood.tga
		tcgen environment
		rgbgen wave sin .12 .2 0 0
	}
	{
		map textures/phantgothic/phantgothic_wood_001_wet.tga
		blendFunc GL_ZERO GL_SRC_ALPHA
		tcmod scale .2 .2
		rgbgen identity	
	}
	{
		map textures/phantgothic/phantgothic_wood_001_wet.tga
		blendFunc GL_ONE GL_SRC_ALPHA
		rgbgen identity	
	}
	{
		map $lightmap
       	blendfunc gl_dst_color gl_zero
		rgbgen identity 
	}
}

textures/phantgothic/phantgothic_jp_fx
{
	surfaceparm nodamage
	q3map_surfacelight 600
	nopicmip
	{
		clampmap textures/phantgothic/phantgothic_jp_fx.tga
		blendFunc GL_ONE GL_ONE
        tcMod rotate 75
	}
}

textures/phantgothic/phantgothic_jp_orange_fx
{
	surfaceparm nodamage
	q3map_surfacelight 600
	nopicmip
	{
		clampmap textures/phantgothic/phantgothic_jp_orange_fx.tga
		blendFunc GL_ONE GL_ONE
        tcMod rotate 75
	}
}

textures/phantgothic/phantgothic_portal
{
	qer_editorimage textures/phantgothic/phantgothic_portal_3.tga
	qer_trans .5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	nopicmip
	cull disable
	{ 
		clampmap textures/phantgothic/phantgothic_portal_3.tga
		blendFunc Blend
		rgbgen identity
		tcMod rotate 25
	}
	{ 
		clampmap textures/phantgothic/phantgothic_portal_3.tga
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

textures/phantgothic/phantgothic_portal_orange
{
	qer_editorimage textures/phantgothic/phantgothic_portal_orange.tga
	qer_trans .75
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	q3map_surfacelight 100
	q3map_lightimage textures/ctf2/orangeteam01.tga
	nopicmip
	cull disable
	{ 
		clampmap textures/phantgothic/phantgothic_portal_orange.tga
		blendFunc Blend
		rgbgen identity
		tcMod rotate 25
	}
	{ 
		clampmap textures/phantgothic/phantgothic_portal_orange.tga
		blendFunc Blend
		rgbgen identity
		tcMod rotate 75
		tcMod stretch sin .5 .45 .1 .1
	}
}

textures/phantgothic/phantgothic_rings
{
	qer_editorimage textures/phantgothic/phantgothic_rings.tga
	surfaceparm alphashadow
   	surfaceparm trans	
	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map textures/phantgothic/phantgothic_rings.tga
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

textures/phantgothic/phantgothic_rain
{
	qer_editorimage textures/phantgothic/phantgothic_rain_editor.tga
    surfaceparm trans	
    surfaceparm nomarks	
    surfaceparm nonsolid
	surfaceparm nolightmap
    qer_trans .5
	cull none      
	{
		map textures/phantgothic/phantgothic_rain.tga
                tcMod Scroll .1 -4
                tcMod turb .1 .25 0 -.1
                blendFunc GL_ONE GL_ONE
        }
}

textures/phantgothic/phantgothic_sky_001
{
	skyparms - 512 -
	q3map_lightImage textures/phantgothic/phantgothic_sky_001.tga
	q3map_sunExt .77 .91 1 75 80 60 3 16
	q3map_lightmapFilterRadius 0 16		//self other
	q3map_skyLight 108 4
	surfaceparm sky
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nodlight
	nopicmip
	nomipmaps
	qer_editorimage textures/phantgothic/phantgothic_sky_001.tga
	{
		map textures/phantgothic/phantgothic_sky_001.tga
		tcMod scale 8 8
		tcMod scroll .02 .05
		depthWrite
	}
	{
		map textures/phantgothic/phantgothic_sky_001.tga
		blendFunc GL_ONE GL_ONE
		tcMod scale 4 4
		tcMod scroll 0.03 0.05
	}
} 

textures/phantgothic/phantgothic_window_light
{
	surfaceparm nolightmap
	surfaceparm nodlight
	surfaceparm nomarks
	qer_editorimage textures/phantgothic/phantgothic_window_light.tga
	{
		map textures/phantgothic/phantgothic_window_light.tga
	}
} 

textures/phantgothic/tp_metal_fence_grate
{
	surfaceparm alphashadow
	surfaceparm metalsteps
	surfaceparm nomarks
	surfaceparm trans
	cull disable
	nopicmip
	{
		map textures/phantgothic/tp_metal_fence_grate.tga
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

textures/phantgothic/tp_metal_fence_grate_nonsolid
{
	qer_editorimage textures/phantgothic/tp_metal_fence_grate.tga
	surfaceparm alphashadow
	surfaceparm metalsteps
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nonsolid
	cull disable
	nopicmip
	{
		map textures/phantgothic/tp_metal_fence_grate.tga
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


textures/phantgothic/tp_spiderweb_001
{
	qer_editorimage textures/phantgothic/tp_spiderweb_001.tga
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nonsolid
	//qer_trans 0.5
	cull none
	tessSize 32
    deformVertexes wave 194 sin 0 3 0 .4
    deformVertexes normal .3 .2
	{
		map textures/phantgothic/tp_spiderweb_001.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}
}

textures/phantgothic/tp_spiderweb_004
{
	qer_editorimage textures/phantgothic/tp_spiderweb_004.tga
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nonsolid
	//qer_trans 0.5
	cull none
	tessSize 32
    deformVertexes wave 194 sin 0 3 0 .4
    deformVertexes normal .3 .2
	{
		map textures/phantgothic/tp_spiderweb_004.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}
}

textures/phantgothic/tp_spiderweb_005
{
	qer_editorimage textures/phantgothic/tp_spiderweb_005.tga
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nonsolid
	//qer_trans 0.5
	cull none
	tessSize 32
    deformVertexes wave 194 sin 0 3 0 .4
    deformVertexes normal .3 .2
	{
		map textures/phantgothic/tp_spiderweb_005.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}
}

textures/phantgothic/phantgothic_torchlight
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

textures/phantgothic/phantgothic_stainedglass_001
{
   qer_editorimage textures/phantgothic/phantgothic_stainedglass_001.tga
   surfaceparm lightfilter
   surfaceparm nolightmap
   cull disable
   q3map_lightmapFilterRadius 0 4
   q3map_surfacelight 100
   {
      map textures/phantgothic/phantgothic_stainedglass_001.tga
      blendFunc GL_DST_COLOR GL_ZERO
      rgbGen identity
   }
}

textures/phantgothic/phantgothic_stainedglass_002
{
   qer_editorimage textures/phantgothic/phantgothic_stainedglass_002.tga
   surfaceparm lightfilter
   surfaceparm nolightmap
   cull disable
   q3map_lightmapFilterRadius 0 4
   q3map_surfacelight 100
   {
      map textures/phantgothic/phantgothic_stainedglass_002.tga
      blendFunc GL_DST_COLOR GL_ZERO
      rgbGen identity
   }
}

textures/phantgothic/phantgothic_stainedglass_003
{
   qer_editorimage textures/phantgothic/phantgothic_stainedglass_003.tga
   surfaceparm lightfilter
   surfaceparm nolightmap
   cull disable
   q3map_lightmapFilterRadius 0 4
   q3map_surfacelight 100
   {
      map textures/phantgothic/phantgothic_stainedglass_003.tga
      blendFunc GL_DST_COLOR GL_ZERO
      rgbGen identity
   }
}
textures/phantgothic/phantgothic_stainedglass_004
{
	qer_editorimage textures/phantgothic/phantgothic_stainedglass_002.tga
	q3map_lightimage textures/phantgothic/phantgothic_stainedglass_002.tga
	q3map_surfacelight 200
	q3map_bounceScale 64
	{
		map textures/phantgothic/phantgothic_stainedglass_002.tga
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/phantgothic/phantgothic_window_002
{
	qer_editorimage textures/phantgothic/phantgothic_window_002.tga
	q3map_lightimage textures/phantgothic/phantgothic_window_002.tga
	q3map_surfacelight 500
	{
		map textures/phantgothic/phantgothic_window_002.tga
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/phantgothic/phantgothic_window_002_100
{
	qer_editorimage textures/phantgothic/phantgothic_window_002.tga
	q3map_lightimage textures/phantgothic/phantgothic_window_002.tga   
	surfaceparm lightfilter
    q3map_lightmapFilterRadius 0 4
	q3map_surfacelight 100
	{
		map textures/phantgothic/phantgothic_window_002.tga
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/phantgothic/phantgothic_window_002_1000
{
	qer_editorimage textures/phantgothic/phantgothic_window_002.tga
	q3map_lightimage textures/phantgothic/phantgothic_window_002.tga   
	surfaceparm lightfilter
    q3map_lightmapFilterRadius 0 4
	q3map_surfacelight 1000
	{
		map textures/phantgothic/phantgothic_window_002.tga
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/phantgothic/phant_brick_arch_nonsolid
{
	qer_editorimage textures/phantgothic/phant_brick_arch.tga
	surfaceparm nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantgothic/phant_brick_arch.tga
		blendfunc filter
	}
}

textures/phantgothic/phant_02_trim_02_nonsolid
{
	qer_editorimage textures/phantgothic/phant_02_trim_02.tga
	surfaceparm nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantgothic/phant_02_trim_02.tga
		blendfunc filter
	}
}

textures/phantgothic/phantgothic_trim_003_nonsolid
{
	qer_editorimage textures/phantgothic/phantgothic_trim_003.tga
	surfaceparm nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantgothic/phantgothic_trim_003.tga
		blendfunc filter
	}
}

textures/phantgothic/phantgothic_trim_008_scale_2_2
{
	qer_editorimage textures/phantgothic/phantgothic_trim_008_scale_2_2.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantgothic/phantgothic_trim_008.tga
		tcmod scale 2 2
		blendfunc filter
	}
}

textures/phantgothic/phantgothic_trim_008_scale_2_2_nonsolid
{
	qer_editorimage textures/phantgothic/phantgothic_trim_008_scale_2_2.tga
	surfaceparm nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantgothic/phantgothic_trim_008.tga
		tcmod scale 2 2
		blendfunc filter
	}
}

textures/phantgothic/phantgothic_trim_008_nonsolid
{
	qer_editorimage textures/phantgothic/phantgothic_trim_008.tga
	surfaceparm nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantgothic/phantgothic_trim_008.tga
		tcmod scale 2 2
		blendfunc filter
	}
}
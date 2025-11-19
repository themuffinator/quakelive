// q3wcp14 "spider crossings" shader
////////////////////////////////////////////////////////////////////////
// 
////////////////////////////////////////////////////////////////////////
textures/camper/clang_clip
{
	qer_editorimage textures/common/nolightmap.tga
	qer_trans 0.40
	surfaceparm nodraw
	surfaceparm playerclip
 	surfaceparm metalsteps	   
}
////////////////////////////////////////////////////////////////////////
// sky
////////////////////////////////////////////////////////////////////////
textures/camper/s_camper_sky
{
	qer_editorimage textures/skies/pjbasesky.tga
			
//	q3map_sunExt 1 1 1 145 45 55 3 16
//	q3map_lightmapFilterRadius 0 16
//	q3map_skyLight 127 3

	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	q3map_lightsubdivide 512 
	// q3map_sun <red> <green> <blue> <intensity> <degrees> <elevation>
//	q3map_sun	0.266383 0.274632 0.358662 100 315 85
	q3map_sunExt 0.266383 0.274632 0.358662 100 315 85 3 16
	q3map_lightmapFilterRadius 0 16
	q3map_surfacelight 100
	q3map_skyLight 127 3

	skyparms - 200 -
	
	{
		map textures/skies/dimclouds.tga
		tcMod scroll 0.015 0.016
		tcMod scale 3 3
		depthWrite
	}
	{
		map textures/skies/pjbasesky.tga
		blendfunc add
		tcMod scroll -0.01 -0.012
		tcMod scale 5 5
	}
}
////////////////////////////////////////////////////////////////////////
// combined texture - shader
////////////////////////////////////////////////////////////////////////
// -- red metal + light beam
textures/camper/s_xian_dm3padwall_red
{
	q3map_surfacelight 100
	q3map_lightimage textures/camper/s_padmetglow_red.tga
	qer_editorimage textures/camper/s_padmet.tga

	{
		map textures/camper/s_padmet.tga
		rgbGen identity
	}	
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
	}

	{
		map textures/camper/s_padmetglow_red.tga
		blendfunc add
		rgbgen wave sin 0 1 0 .5
		tcmod scale 1 .05
		tcmod scroll 0 1
	}

}
// -- blue metal + light beam
textures/camper/s_xian_dm3padwall_blue
{
	q3map_surfacelight 100
	q3map_lightimage textures/camper/s_padmetglow_blue.tga
	qer_editorimage textures/camper/s_padmet.tga


	{
		map textures/camper/s_padmet.tga
		rgbGen identity
	}	
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
	}
	{
		map textures/camper/s_padmetglow_blue.tga
		blendfunc add
		rgbgen wave sin 0 1 0 .5
		tcmod scale 1 .05
		tcmod scroll 0 1
	}

}
////////////////////////////////////////////////////////////////////////
// techwall -- red 'glow' variant
textures/camper/s_red_xian_dm3padwall
{
	q3map_surfacelight 100
	q3map_lightimage textures/camper/s_xian_padmetglow_red.tga
	qer_editorimage textures/sfx/xian_dm3padwall.tga
	
	{
		map textures/sfx/xian_dm3padwall.tga
		rgbGen identity
	}
	
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
	}
	{
		map textures/camper/s_xian_padmetglow_red.tga
		blendfunc add
		rgbgen wave sin 0 1 0 .5
		tcmod scale 1 .05
		tcmod scroll 0 1
	}
}
////////////////////////////////////////////////////////////////////////
// water variant
////////////////////////////////////////////////////////////////////////
textures/camper/scan_dirtwater
	{
		qer_editorimage textures/liquids/pool3d_3.tga
		qer_trans .5
		q3map_globaltexture
		surfaceparm trans
		surfaceparm nonsolid
		surfaceparm water
		q3map_surfacelight 50
		cull disable
		deformVertexes wave 64 sin .5 .5 0 .5	
		{ 
			map textures/liquids/pool3d_5.tga
			blendfunc GL_dst_color GL_one
			rgbgen identity
			tcmod scale .5 .5
			tcmod transform 1.5 0 1.5 1 1 2
			tcmod scroll -.05 .001
		}
		{ 
			map textures/liquids/pool3d_6.tga
			blendfunc GL_dst_color GL_one
			rgbgen identity
			tcmod scale .5 .5
			tcmod transform 0 1.5 1 1.5 2 1
			tcmod scroll .025 -.001
		}
		{
			map $lightmap
			blendfunc filter
			rgbgen identity		
		}

}
////////////////////////////////////////////////////////////////////////
// 
////////////////////////////////////////////////////////////////////////
// re-adjusting surface light for id shader
textures/camper/s_patch10_pj_lite
{
        qer_editorimage textures/base_light/patch10_pj_lite.tga
	q3map_surfacelight 600
	surfaceparm nomarks
//	light 1
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/patch10_pj_lite.tga
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/base_light/patch10_pj_lite.blend.tga
		blendfunc add
	}
}
////////////////////////////////////////////////////////////////////////
// light source
////////////////////////////////////////////////////////////////////////

// id's with less light
textures/camper/s_skylight1
{
	qer_editorimage textures/base_floor/skylight1.tga
	q3map_lightimage textures/base_floor/skylight1_lm.tga
	q3map_surfacelight 30
	
        {
		map $lightmap
		rgbGen identity
	}
        {
		map textures/base_floor/skylight1.tga
		blendfunc filter
                rgbGen identity
	}	
        {
		map textures/base_floor/skylight1_lm.tga
		blendfunc add
                rgbgen wave triangle .2 2 0 7.7
	}
        {
		map textures/base_floor/skylight1_lm.tga
		blendfunc add
                rgbgen wave triangle .2 5 1 5.1
	}
    	
}
////////////////////////////////////////////////////////////////////////
// base logos
////////////////////////////////////////////////////////////////////////
textures/camper/s_redbase
{
	q3map_lightimage textures/camper/s_redbase.tga
        q3map_surfacelight 100
	{
		map textures/camper/s_redbase.tga
	        rgbGen wave square 0 1 0 .5
	}
	{
		map textures/base_wall/comp3text.tga
		blendfunc add
	        rgbGen identity
		tcmod scroll 3 3
	}
	{
		map textures/base_wall/comp3textb.tga
		blendfunc add
	        rgbGen identity
		tcmod scroll 3 3
	}
	{
		map $lightmap
	        rgbGen identity
		blendfunc filter
	}
	{
		map $lightmap
		tcgen environment
		tcmod scale .5 .5
	        rgbGen wave sin .25 0 0 0
		blendfunc add
	}	          		
}     
textures/camper/s_bluebase
{
	q3map_lightimage textures/camper/s_bluebase.tga
        q3map_surfacelight 100
	{
		map textures/camper/s_bluebase.tga
	        rgbGen wave square 0 1 0 .5
	}
	{
		map textures/base_wall/comp3text.tga
		blendfunc add
	        rgbGen identity
		tcmod scroll 3 3
	}
	{
		map textures/base_wall/comp3textb.tga
		blendfunc add
	        rgbGen identity
		tcmod scroll 3 3
	}
	{
		map $lightmap
	        rgbGen identity
		blendfunc filter
	}
	{
		map $lightmap
		tcgen environment
		tcmod scale .5 .5
	        rgbGen wave sin .25 0 0 0
		blendfunc add
	}	          		
}     
////////////////////////////////////////////////////////////////////////
// metal variant for red side
////////////////////////////////////////////////////////////////////////
textures/camper/s_redmetal2b
{
	qer_editorimage textures/camper/redmetal2b.tga
	q3map_surfacelight 100
	q3map_lightimage textures/camper/redmetal2bglow.tga


	{
		map textures/base_wall/chrome_env.tga
	        rgbGen identity
		tcGen environment
		tcmod scale .25 .25
	}
	
	{
		map textures/camper/redmetal2b.tga
		blendfunc GL_ONE_MINUS_SRC_ALPHA GL_SRC_ALPHA	
		rgbGen identity
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}


	{
		map textures/camper/redmetal2bglow.tga
		blendfunc add
		rgbGen wave sin 0.5 0.5 0 .2
	}
}
////////////////////////////////////////////////////////////////////////
// metal variant for red side
////////////////////////////////////////////////////////////////////////
textures/camper/s_pjgrate1
{
	qer_editorimage textures/camper/s_pjgrate1.tga

	surfaceparm	metalsteps		
	surfaceparm	trans
	cull none

	// A GRATE THAT CAN BE SEEN FROM BOTH SIDES
	{
		map textures/camper/s_pjgrate1.tga
		tcMod scale 2 2
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
}

// for t-juncs on jp's
textures/camper/camper_jptrim
{     
        {
                map textures/effects/tinfx.tga       
                tcGen environment
                rgbGen identity
	}   
        {
		map textures/camper/camper_jptrim.tga
                blendfunc blend
		rgbGen identity
	} 
        {
		map $lightmap
                blendfunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
}
////////////////////////////////////////////////////////////////////////
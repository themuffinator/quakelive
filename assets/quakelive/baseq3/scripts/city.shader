textures/city/s_yucksky
{
	qer_editorimage textures/city/s_yuck.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky
	q3map_sunExt 1.000000 0.615385 0.282051 100 50 70 3 16
	q3map_lightmapFilterRadius 0 16
	q3map_skyLight 127 3
	skyparms - 256 -
	{
		map textures/city/s_yuck.tga
		tcMod scroll 0.015 0.016
		tcMod scale 3 3
		depthWrite
	}
	{
		map textures/city/s_yuck.tga
		blendFunc gl_one gl_one
		tcMod scroll 0.01 0.012
		tcMod scale 5 5
	}
}

textures/city/s_yucksky2
{
	qer_editorimage textures/city/s_yuck.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky
	q3map_sunExt 1.000000 0.615385 0.282051 100 230 70 3 16
	q3map_lightmapFilterRadius 0 16
	q3map_skyLight 127 3
	skyparms - 256 -
	{
		map textures/city/s_yuck.tga
		tcMod scroll 0.015 0.016
		tcMod scale 3 3
		depthWrite
	}
	{
		map textures/city/s_yuck.tga
		blendFunc gl_one gl_one
		tcMod scroll 0.01 0.012
		tcMod scale 5 5
	}
}

textures/city/s_yuckfog
{
	qer_editorimage textures/sfx/fog_red.tga
	surfaceparm	trans
	surfaceparm	nonsolid
	surfaceparm	fog
	surfaceparm 	nolightmap
	q3map_surfacelight 30
	fogparms ( .6 .1 .05 ) 400
}

textures/city/s_yuckfog_water
{
	qer_editorimage textures/sfx/fog_red.tga
	surfaceparm	trans
	surfaceparm	nonsolid
	surfaceparm	fog
	surfaceparm 	nolightmap
	fogparms ( .3 .05 .01 ) 700
}

textures/city/s_yuckfog_blue
{
	qer_editorimage textures/sfx/fog_blue.tga
	surfaceparm	trans
	surfaceparm	nonsolid
	surfaceparm	fog
	surfaceparm 	nolightmap
	q3map_surfacelight 30
	fogparms ( .05 .1 .6 ) 400
}

textures/city/s_yuckfog_blue_water
{
	qer_editorimage textures/sfx/fog_blue.tga
	surfaceparm	trans
	surfaceparm	nonsolid
	surfaceparm	fog
	surfaceparm 	nolightmap
	fogparms ( .01 .05 .3 ) 700
}

textures/city/s_brownfog
{
	qer_editorimage textures/sfx/fog_red.tga
	surfaceparm	trans
	surfaceparm	nonsolid
	surfaceparm	fog
	surfaceparm 	nodrop
	surfaceparm 	nolightmap
	q3map_surfacelight 30
	fogparms ( 0.340908 0.179301 0.134846 ) 600
}


textures/city/s_metal1
{   
	qer_editorimage textures/city/scan_metal1.tga
	{
		map textures/effects/tinfx2b.tga
		tcGen environment
		rgbGen wave sin .5 .1 .1 .3 
	}   
	{
		map textures/city/scan_metal1.tga
        blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}
    {
		map $lightmap
        blendFunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
}

textures/city/s_light1_3K
{
	qer_editorimage textures/city/scan_light1.tga
	q3map_lightimage textures/city/scan_light1_blend.tga
	q3map_surfacelight 3000
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/city/scan_light1.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/city/scan_light1_blend.tga
		rgbGen wave sin .5 .1 .1 .3 
		blendfunc GL_ONE GL_ONE
	}
}

textures/city/scan_light2
{
	qer_editorimage textures/city/scan_light2.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/city/scan_light2.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/city/scan_light2_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/city/s_beam_1
{
	qer_editorimage textures/city/s_beam_red.tga
	surfaceparm trans	
    surfaceparm nomarks	
    surfaceparm nonsolid
	surfaceparm nolightmap
    qer_trans .5
	cull none
	{
		map textures/city/s_beam_red.tga
        tcMod Scroll .3 0
        blendFunc add
    }
}

textures/city/s_beam_2
{
	qer_editorimage textures/city/s_beam_blue.tga
	surfaceparm trans	
    surfaceparm nomarks	
    surfaceparm nonsolid
	surfaceparm nolightmap
    qer_trans .5
	cull none
	{
		map textures/city/s_beam_blue.tga
        tcMod Scroll .3 0
        blendFunc add
    }
}

textures/city/s_id_beamblue
{
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	qer_trans .5
	cull none
	{
		map textures/city/s_id_beamblue.tga
		tcMod Scroll .3 0
		blendFunc add
	}     
}

textures/city/id_redlight_on
{
	qer_editorimage textures/city/id_redlight_on.tga
	q3map_lightimage textures/city/id_redlight_on.tga
	q3map_surfacelight 500
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/city/id_redlight_on.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/city/id_redlight_on.tga
		rgbGen wave sin .3 .1 .7 1.3 
		blendfunc GL_ONE GL_ONE
	}
}

textures/city/id_bluelight_on
{
	qer_editorimage textures/city/id_bluelight_on.tga
	q3map_lightimage textures/city/id_bluelight_on.tga
	q3map_surfacelight 500
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/city/id_bluelight_on.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/city/id_bluelight_on.tga
		rgbGen wave sin .3 .1 .7 1.3 
		blendfunc GL_ONE GL_ONE
	}
}

textures/city/s_ceil1_22a_4k
{
	surfaceparm nomarks
	qer_editorimage textures/base_light/ceil1_22a.tga
	q3map_surfacelight 4000
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_22a.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_22a.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/city/s_ceil1_30_4k
{
	surfaceparm nomarks
	qer_editorimage textures/base_light/ceil1_30
	q3map_surfacelight 4000
	light 1
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_30.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_30.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/city/scan_trim1
{
	qer_editorimage textures/city/scan_trim1.tga
	q3map_lightimage textures/city/scan_trim1_blend.tga
	q3map_surfacelight 100
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/city/scan_trim1.tga
		blendfunc gl_dst_color gl_zero
	}
	{
		map textures/city/scan_trim1_blend.tga
		blendfunc gl_one gl_one
		rgbGen wave sin .8 .3 .1 .1
	}
}


textures/city/scan_trim2
{
	qer_editorimage textures/city/scan_trim2.tga
	q3map_lightimage textures/city/scan_trim2_blend.tga
	q3map_surfacelight 200
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/city/scan_trim2.tga
		blendfunc gl_dst_color gl_zero
	}
	{
		map textures/city/scan_trim2_blend.tga
		blendfunc gl_one gl_one
		rgbGen wave sin .8 .3 .1 .1
	}
}


textures/city/scan_trim2_nolight
{
	qer_editorimage textures/city/scan_trim2.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/city/scan_trim2.tga
		blendfunc gl_dst_color gl_zero
	}
	{
		map textures/city/scan_trim2_blend.tga
		blendfunc gl_one gl_one
		rgbGen wave sin .8 .3 .1 .1
	}
}

textures/city/scan_trim1b
{
	qer_editorimage textures/city/scan_trim1b.tga
	q3map_lightimage textures/city/scan_trim1b_blend.tga
	q3map_surfacelight 100
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/city/scan_trim1b.tga
		blendfunc gl_dst_color gl_zero
	}
	{
		map textures/city/scan_trim1b_blend.tga
		blendfunc gl_one gl_one
		rgbGen wave sin .8 .3 .1 .1
	}
}

textures/city/scan_trim2b
{
	qer_editorimage textures/city/scan_trim2b.tga
	q3map_lightimage textures/city/scan_trim2b_blend.tga
	q3map_surfacelight 200
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/city/scan_trim2b.tga
		blendfunc gl_dst_color gl_zero
	}
	{
		map textures/city/scan_trim2b_blend.tga
		blendfunc gl_one gl_one
		rgbGen wave sin .8 .3 .1 .1
	}
}

textures/city/scan_trim2b_nolight
{
	qer_editorimage textures/city/scan_trim2b.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/city/scan_trim2b.tga
		blendfunc gl_dst_color gl_zero
	}
	{
		map textures/city/scan_trim2b_blend.tga
		blendfunc gl_one gl_one
		rgbGen wave sin .8 .3 .1 .1
	}
}


textures/city/s_steam
{
	qer_editorimage textures/city/steam_fx.tga
	qer_trans 0.4
	cull none
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm pointlight
	deformVertexes wave 50 sin 0 3 0 .3
	deformVertexes move .3 .1 0  sin 0 .5 0 0.2
	{
		map textures/city/steam_fx.tga
		tcmod scroll 0 0.3
		blendFunc blend
		rgbGen vertex
	}
}

textures/city/steam_fx
{
	qer_editorimage textures/city/steam_fx.tga
	qer_trans 0.4
	cull none
	deformVertexes autoSprite2
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm pointlight
	deformVertexes wave 50 sin 0 3 0 .3
	deformVertexes move .3 .1 0  sin 0 .5 0 0.2
	{
		map textures/city/steam_fx.tga
		tcmod scroll 0 0.3
		blendFunc blend
		rgbGen vertex
	}
}

textures/city/s_bluekey
{
	qer_editorimage textures/sfx/metalfloor_wall_5b.tga
	q3map_lightimage textures/sfx/metalfloor_wall_5bglowblu.tga
	surfaceparm nomarks
	q3map_surfacelight 200
	{
		map textures/sfx/metalfloor_wall_7b.tga
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map textures/sfx/metalfloor_wall_5bglowblu.tga
		blendfunc gl_one gl_one
		rgbgen wave sin .5 .5 0 .5
	}
}

textures/city/s_redkey
{
	qer_editorimage textures/sfx/metalfloor_wall_9b.tga
	q3map_lightimage textures/sfx/metalfloor_wall_9bglow.tga
	surfaceparm nomarks
	q3map_surfacelight 200
	{
		map textures/sfx/metalfloor_wall_9b.tga
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map textures/sfx/metalfloor_wall_9bglow.tga
		blendfunc gl_one gl_one
		rgbgen wave sin .5 .5 .5 .5	
	}
}

textures/city/scan_trim3_trans
{
	qer_editorimage textures/city/scan_trim3.tga
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nonsolid
	q3map_surfacelight 200
	{
		map textures/city/scan_trim3.tga
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
}

textures/city/s_light1_trans
{
	qer_editorimage textures/city/scan_light1.tga
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/city/scan_light1.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/city/scan_light1_blend.tga
		rgbGen wave sin .5 .1 .1 .3 
		blendfunc GL_ONE GL_ONE
	}
}

textures/city/city_brown
{	
	surfaceparm nolightmap
	surfaceparm noimpact
	surfaceparm nomarks
	{
		map textures/city/city_brown.tga
	}
}

textures/city/qball147
{
	qer_editorimage textures/proto2/techtrim02.tga
	{
		map textures/city/qball147.tga
	}
}
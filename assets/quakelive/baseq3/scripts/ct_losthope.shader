textures/ct_losthope/fence
{
	surfaceparm trans	
	surfaceparm alphashadow	
	cull none
        nopicmip

	{
		map textures/base_trim/proto_fence.tga
		tcMod scale 3 3
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

textures/ct_losthope/graffiti_big_01
{    
     surfaceparm	nomarks   
     surfaceparm	trans
	 surfaceparm	nonsolid
     surfaceparm pointlight
	nopicmip
   
        {
		map textures/ct_losthope/graffiti_big_01.tga
                blendFunc add
		rgbGen vertex
	}
}

textures/ct_losthope/graffiti_big_02
{    
     surfaceparm	nomarks   
     surfaceparm	trans
	 surfaceparm	nonsolid
     surfaceparm pointlight
	nopicmip
   
        {
		map textures/ct_losthope/graffiti_big_02.tga
                blendFunc add
		rgbGen vertex
	}
}

textures/ct_losthope/graffiti_tag_01
{    
     surfaceparm	nomarks   
     surfaceparm	trans
	 surfaceparm	nonsolid
     surfaceparm pointlight
	nopicmip
   
        {
		map textures/ct_losthope/graffiti_tag_01.tga
                blendFunc add
		rgbGen vertex
	}
}

textures/ct_losthope/hip_stormy
{
	qer_editorimage textures/ct_losthope/env/stormydays_ft.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	q3map_lightsubdivide 256
	q3map_surfacelight 80
	surfaceparm sky
	q3map_sun 1 1 1 100 315 40
	skyparms textures/ct_losthope/env/stormydays - -
}

textures/ct_losthope/jp_wall_01
{
	q3map_surfacelight 100
	q3map_lightimage textures/ct_losthope/jp_wall_01_blend.tga
	qer_editorimage textures/ct_losthope/jp_wall_01.tga
	{
		map textures/ct_losthope/jp_wall_01.tga
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc GL_DST_COLOR GL_ZERO
	}
	{
		map textures/ct_losthope/jp_wall_01_blend.tga
		blendfunc GL_ONE GL_ONE
		rgbgen wave sin 0 1 0 .5
		tcmod scale 1 .05
		tcmod scroll 0 1
	}
}

textures/ct_losthope/jp_wall_02
{
	qer_editorimage textures/ct_losthope/jp_wall_01.tga

	{
		map textures/ct_losthope/jp_wall_01_blend.tga
		rgbGen identity
		tcmod scale 1 .5
		tcmod scroll 0 1.42
	}

	{
		map textures/ct_losthope/jp_wall_01.tga
		blendFunc blend
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc GL_DST_COLOR GL_ZERO
	}	
}

textures/ct_losthope/trim_02_shiny
{   
        qer_editorimage textures/ct_losthope/trim_02.tga
	{
		map textures/ct_losthope/trim_02.tga
		rgbGen identity
	}
	{
        map textures/ct_losthope/tinfx.tga       
        blendFunc add
		tcGen environment
        rgbGen identity
	}   
    {
		map $lightmap
        blendFunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
}

//LAMPS

textures/ct_losthope/lamp_yellow_nolight
{
	surfaceparm nomarks
	qer_editorimage textures/base_light/ceil1_39.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_39.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_39.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_losthope/lamp_green_nolight
{
	qer_editorimage textures/ct_losthope/ceil1_green.tga
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_losthope/ceil1_green.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_losthope/ceil1_green.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_losthope/lamp_red_nolight
{
	qer_editorimage textures/base_light/ceil1_22a.tga
	surfaceparm nomarks
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

textures/ct_losthope/lamp_blue_nolight
{
	qer_editorimage textures/base_light/ceil1_34.tga
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_34.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_34.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

//ITEM SPAWN

textures/ct_losthope/item_spawn_01
{
   	surfaceparm nonsolid
	surfaceparm nomarks	
    nopicmip
	qer_editorimage textures/ct_losthope/item_spawn_01.tga
	{
		map textures/ct_losthope/item_spawn_01.tga
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
	{
		map textures/ct_losthope/item_spawn_01_blend.tga
		blendfunc add
	}
}

//GRATES

textures/ct_losthope/grate_03_trans
{
    surfaceparm trans		
	qer_editorimage textures/ct_losthope/grate_03.tga
	cull none
    nopicmip
	surfaceparm alphashadow

	{
		map textures/ct_losthope/grate_03.tga
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

//GLASS

textures/ct_losthope/glass_01
{   
    qer_editorimage textures/ct_losthope/glass_01.tga
	surfaceparm trans	
	cull none
	qer_trans 	0.5
	sort 7
	{
		map textures/ct_losthope/glass_01.tga
		blendFunc GL_ONE GL_ONE
		rgbGen identity
	}
	{
        map textures/ct_losthope/tinfx.tga       
        blendFunc add
		tcGen environment
        rgbGen identity
	}   
    {
		map $lightmap
        blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/ct_losthope/glass_02
{
	qer_editorimage textures/ct_losthope/glass_blend.tga
	surfaceparm nomarks
	q3map_surfacelight 800
	q3map_lightimage textures/ct_losthope/glass_blend.tga
	sort 7
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_losthope/glass.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_losthope/glass_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_losthope/lightbeam_01_red
{
	qer_editorimage textures/ct_losthope/lightbeam_01.tga
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_losthope/lightbeam_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_losthope/lightbeam_01_red.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_losthope/smoke
{    
     surfaceparm	nomarks   
     surfaceparm	trans
	 surfaceparm	nonsolid
     surfaceparm pointlight
	nopicmip
	deformVertexes autosprite
	deformVertexes wave 100 sin 3 2 .1 0.1
   
        {
		map textures/ct_losthope/smoke.tga
                blendFunc add
		rgbGen vertex
		
		tcmod scroll .01 -.01
	}
}

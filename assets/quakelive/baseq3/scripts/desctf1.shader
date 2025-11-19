textures/desctf1/largerblock3b3dim_wet
{ 
	qer_editorimage textures/gothic_floor/largerblock3b3dim.tga
	{
		map textures/phantgothic/phantgothic_env_wood.tga
		tcgen environment
		rgbgen wave sin .12 .2 0 0
	}
	{
		map textures/desctf1/largerblock3b3dim.tga
		blendFunc GL_ZERO GL_SRC_ALPHA
		tcmod scale .2 .2
		rgbgen identity	
	}
	{
		map textures/desctf1/largerblock3b3dim.tga
		blendFunc GL_ONE GL_SRC_ALPHA
		rgbgen identity	
	}
	{
		map $lightmap
        blendfunc gl_dst_color gl_zero
		rgbgen identity 
	}
}


textures/desctf1/phantgothic_jp_fx_red
{
	surfaceparm nodamage
	q3map_surfacelight 600

	{
		clampmap textures/desctf1/phantgothic_jp_fx_red.tga
		blendFunc GL_ONE GL_ONE
	    tcMod rotate 75
	}
}

textures/desctf1/phantgothic_jp_fx_blue
{
	surfaceparm nodamage
	q3map_surfacelight 600
	nopicmip
	{
		clampmap textures/desctf1/phantgothic_jp_fx_blue.tga
		blendFunc GL_ONE GL_ONE
	    tcMod rotate 75
	}
}

textures/desctf1/des_pennant_red
{
	surfaceparm nonsolid
    surfaceparm nomarks
	surfaceparm alphashadow
	nopicmip
	qer_trans 0.99
    cull none
    {
		map textures/desctf1/des_pennant_red.tga
		blendfunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphafunc GE128
		depthwrite
		rgbGen identity
	}
	{
		map $lightmap
        blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
		depthfunc equal
	}
}

textures/desctf1/des_pennant_blue
{
	surfaceparm nonsolid
    surfaceparm nomarks
	surfaceparm alphashadow
	nopicmip
	qer_trans 0.99
    cull none
    {
		map textures/desctf1/des_pennant_blue.tga
		blendfunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphafunc GE128
		depthwrite
		rgbGen identity
	}
    {
		map $lightmap
        blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
		depthfunc equal
	}
}

textures/desctf1/des_rope
{
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	nopicmip
	qer_trans 0.99
	cull none
    {
		map textures/desctf1/des_rope.tga
		blendfunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphafunc GE128
		depthwrite
		rgbGen identitylighting
	}
    {
		map $lightmap
		rgbGen identity
        blendFunc GL_DST_COLOR GL_ZERO
		depthfunc equal
	}
}

textures/desctf1/phantgothic_window_002_red
{
	qer_editorimage textures/desctf1/phantgothic_window_002_red.tga
	q3map_lightimage textures/desctf1/phantgothic_window_002_red.tga
	q3map_surfacelight 500
	{
		map textures/desctf1/phantgothic_window_002_red.tga
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/desctf1/phantgothic_window_002_blue
{
	qer_editorimage textures/desctf1/phantgothic_window_002_blue.tga
	q3map_lightimage textures/desctf1/phantgothic_window_002_blue.tga
	q3map_surfacelight 500
	{
		map textures/desctf1/phantgothic_window_002_blue.tga
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/desctf1/pathmarker_blue
{
	qer_editorimage textures/desctf1/pathmarker_blue
	nopicmip
	surfaceparm nonsolid
	surfaceparm nomarks
	polygonoffset
	{
		map textures/desctf1/pathmarker_blue.tga
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

textures/desctf1/pathmarker_red
{
	qer_editorimage textures/desctf1/pathmarker_red
	nopicmip
	surfaceparm nonsolid
	surfaceparm nomarks
	polygonoffset
	{
		map textures/desctf1/pathmarker_red.tga
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

textures/desctf1/itemmarker_blue
{
	qer_editorimage textures/desctf1/itemmarker_blue
	nopicmip
	surfaceparm nonsolid
	polygonoffset
	{
		clampmap textures/desctf1/itemmarker_blue.tga
		blendFunc GL_ONE GL_ONE
		tcMod rotate 100
	}
}

textures/desctf1/itemmarker_red
{
	qer_editorimage textures/desctf1/itemmarker_red
	nopicmip
	surfaceparm nonsolid
	polygonoffset
	{
		clampmap textures/desctf1/itemmarker_red.tga
		blendFunc GL_ONE GL_ONE
		tcMod rotate 100
	}
}

textures/desctf1/portal
{
	qer_editorimage textures/desctf1/portalfx.tga
	portal
	surfaceparm nolightmap
	surfaceparm nomarks
	{
		map textures/desctf1/portalfx.tga
		blendfunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphagen portal 512
		tcMod scroll 0 -.75
		tcMod turb 0 .1 0 .5
		rgbGen identityLighting	
		depthwrite
	}
}

textures/desctf1/portal_512
{
	qer_editorimage textures/desctf1/portalfx.tga
	portal
	surfaceparm nolightmap
	surfaceparm nomarks
	{
		map textures/desctf1/portalfx.tga
		blendfunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphagen portal 512
		tcMod scroll 0 -.75
		tcMod turb 0 .1 0 .5
		rgbGen identityLighting	
		depthwrite
	}
}

textures/desctf1/portal_256
{
	qer_editorimage textures/desctf1/portalfx.tga
	portal
	surfaceparm nolightmap
	surfaceparm nomarks
	{
		map textures/desctf1/portalfx.tga
		blendfunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphagen portal 256
		tcMod scroll 0 -.75
		tcMod turb 0 .1 0 .5
		rgbGen identityLighting	
		depthwrite
	}
}

textures/desctf1/arrow_blue
{
	qer_editorimage textures/ql/arrow
	nopicmip
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	polygonoffset
	{
		map textures/ql/arrow.tga
		rgbGen const ( .05 .1 .4 )
		blendFunc add
	}
}

textures/desctf1/arrow_red
{
	qer_editorimage textures/ql/arrow
	nopicmip
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	polygonoffset
	{
		map textures/ql/arrow.tga
		rgbGen const ( .8 .15 .15 )
		blendFunc add
	}
}

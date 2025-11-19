// Sky
textures/skies/meth_clouds_delirium
{
	qer_editorimage textures/skies/meth_clouds.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky
	surfaceparm nodlight

	q3map_sunExt 1 0.86 0.76 50 270 75 0.5 16
	q3map_skylight 30 5

	q3map_lightmapSampleSize 32

	q3map_lightImage textures/skies/meth_clouds.tga
	skyparms - 512 -
	{
		map textures/skies/meth_clouds.tga
		tcMod scale 3 2
		tcMod scroll 0.04 0.04
		depthWrite
	}
	{
		map textures/skies/meth_clouds2.tga
		blendfunc GL_ONE GL_ONE
		tcMod scale 10 10
		tcMod scroll .1 .1
	}
	{
		map textures/skies/topclouds.tga
		blendFunc GL_ONE GL_ONE
		tcMod scale 3 3
		tcMod scroll 0.09 0.09
	}
}

// Portals

textures/sfx/portal_delirium_blue
{
	qer_editorimage textures/bst_delirium/portaledge_delirium_blue.jpg
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm trans
	nopicmip
	novlcollapse
	{
		map textures/sfx/portalnoise.jpg
		blendfunc add
		rgbGen identityLighting	
		tcmod scale 1.2 1.2
		tcmod scroll .01 -.11
		rgbgen wave sin 0.95 0.07 0 .85
	}
	{
		map textures/sfx/portal_sfx2.png
		blendfunc GL_DST_COLOR GL_ZERO
		tcmod scale 1 0.9
		tcMod stretch sin 2.65 0.2 0 0.2
		tcMod turb 1 0.1 0 0.1
		tcMod rotate 360
	}
	{
		map textures/sfx/portal_sfx2.png
		blendfunc GL_DST_COLOR GL_ZERO
		tcmod scale 1 1
		tcMod stretch sin 2.5 0.1 0 0.2
		tcMod turb 1 -0.1 0 0.1
		tcMod rotate 355
	}
	{
		map textures/bst_delirium/portaledge_delirium_blue.jpg
		blendfunc GL_DST_COLOR GL_ZERO
		tcmod scale 0.5 0.5
		tcmod scroll -.01 -0.11
	}
}

textures/sfx/portal_delirium_red
{
	qer_editorimage textures/bst_delirium/portaledge_delirium_red.jpg
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm trans
	nopicmip
	novlcollapse
	{
		map textures/bst_delirium/portalnoise_delirium.jpg
		blendfunc add
		rgbGen identityLighting	
		tcmod scale 1.2 1.2
		tcmod scroll .01 -.11
		rgbgen wave sin 0.95 0.07 0 .85
	}
	{
		map textures/sfx/portal_sfx2.png
		blendfunc GL_DST_COLOR GL_ZERO
		tcmod scale 1 0.9
		tcMod stretch sin 2.65 0.2 0 0.2
		tcMod turb 1 0.1 0 0.1
		tcMod rotate 360
	}
	{
		map textures/sfx/portal_sfx2.png
		blendfunc GL_DST_COLOR GL_ZERO
		tcmod scale 1 1
		tcMod stretch sin 2.5 0.1 0 0.2
		tcMod turb 1 -0.1 0 0.1
		tcMod rotate 355
	}
	{
		map textures/bst_delirium/portaledge_delirium_red.jpg
		blendfunc GL_DST_COLOR GL_ZERO
		tcmod scale 0.5 0.5
		tcmod scroll -.01 -0.11
	}
}

// Support

textures/proto2/v_support02_delirium
{
	qer_editorimage textures/bst_delirium/v_support02_delirium.png
	surfaceparm alphashadow
	cull none
        nomipmaps
	{
		map textures/bst_delirium/v_support02_delirium.png
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

// Lights

textures/base_light/ceil1_38_3_trans
{
	qer_editorimage textures/base_light/ceil1_38.tga
	surfaceparm nomarks
	surfaceparm nonsolid
	q3map_surfacelight 3000
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_38.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_38.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

// Zap

textures/sfx/zap_scrollblue1000_delirium
{
        q3map_surfacelight	1000
        surfaceparm	trans
	surfaceparm nomarks
	surfaceparm nolightmap
	q3map_lightimage textures/sfx/zap_scrollblue.tga
	qer_editorimage textures/sfx/zap_scroll2blue.tga
	cull none
	
	{
		map textures/sfx/zap_scrollblue.tga
		blendFunc GL_ONE GL_ONE
                rgbgen wave triangle .8 2 0 7
				tcMod scale  2 2
                tcMod scroll 0 0.5
	}	
        {
		map textures/sfx/zap_scroll2blue.tga
		blendFunc GL_ONE GL_ONE
                rgbgen wave triangle 1 1.4 0 6.3
                tcMod scale  -2 2
                tcMod scroll 2 0.5
	}	
        {
		map textures/sfx/zap_scroll2blue.tga
		blendFunc GL_ONE GL_ONE
                rgbgen wave triangle 1 1.4 0 7.7
				tcMod scale  2 2
                tcMod scroll -1.3 0.5
	}	
}
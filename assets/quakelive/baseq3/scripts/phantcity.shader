//WINDOW

textures/phant_cityy/window_01
{
   	surfaceparm nonsolid
	surfaceparm nomarks	
    nopicmip
	qer_editorimage textures/phant_cityy/window_01.tga
	{
		map textures/phant_cityy/window_01.tga
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
		map textures/phant_cityy/window_01_blend.tga
		blendfunc add
	}
}

textures/phant_cityy/window_02
{
   	surfaceparm nonsolid
	surfaceparm nomarks	
    nopicmip
	qer_editorimage textures/phant_cityy/window_02.tga
	{
		map textures/phant_cityy/window_02.tga
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
		map textures/phant_cityy/window_02_blend.tga
		blendfunc add
	}
}

textures/phant_cityy/window_03
{
	surfaceparm nomarks	
	cull none
    q3map_lightmapFilterRadius 0 16
    q3map_surfacelight 120
    nopicmip
	qer_editorimage textures/phant_cityy/window_03.tga
	{
		map textures/effects/envmap2.tga
     	tcGen environment
    	tcmod scale 4 4
    	rgbGen identity
    	blendFunc GL_DST_COLOR GL_ONE
	}
	{
		map textures/phant_cityy/window_03_border.tga
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
		map textures/phant_cityy/window_03.tga
		blendFunc GL_DST_COLOR GL_SRC_ALPHA
		rgbGen identity
		alphaGen lightingSpecular
    }
}

textures/phant_cityy/window_04
{
	surfaceparm nomarks	
	cull none
    q3map_lightmapFilterRadius 0 16
    q3map_surfacelight 120
    nopicmip
	qer_editorimage textures/phant_cityy/window_04.tga
	{
		map textures/phant_cityy/window_04.tga
		blendFunc GL_DST_COLOR GL_SRC_ALPHA
		rgbGen identity
		alphaGen lightingSpecular
    }
	{
		map textures/effects/envmap2.tga
     	tcGen environment
    	tcmod scale 4 4
    	rgbGen identity
    	blendFunc GL_DST_COLOR GL_ONE
	}
	{
		map textures/phant_cityy/window_04_border.tga
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

//LIGHTS

textures/phant_cityy/ironcrossblue_nolight
{
	qer_editorimage textures/gothic_light/ironcrossltblue.tga
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/gothic_light/ironcrossltblue.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/gothic_light/ironcrossltblue.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

//JUMPPAD

textures/phant_cityy/jp_01
{

	surfaceparm nodamage
	{
		map textures/phant_cityy/jp_01.tga
		rgbGen identity
	}
	
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
	}
	
	{
		map textures/phant_cityy/bouncepad01b_layer1_teal.tga
		blendfunc add
		rgbGen wave sin .5 .5 0 1.5	
	}

	{
		clampmap textures/phant_cityy/jp_01_ring.tga
		blendfunc add
		tcMod stretch sin 1.2 .8 0 1.5
		rgbGen wave square .5 .5 .25 1.5
	}

}

// -----------------------------------------------------------
// sky
// must be compiled with -skyfix in BSP phase using Q3Map2
// to fix ATI/correct texture clamping issue
// powered by shaderlab
// -----------------------------------------------------------

textures/phant_cityy/sky
{
	qer_editorimage textures/phant_cityy/env/sky_dark.tga
	q3map_lightImage textures/phant_cityy/env/sky_dark.tga

	q3map_sunExt 1 1 1 200 -30 45 2 12
	q3map_skyLight 75 3
	
	surfaceparm sky
	surfaceparm noimpact
	surfaceparm nolightmap
	
	skyparms textures/phant_cityy/env/sky 1337 -
	
	nopicmip
	
	{
		map textures/phant_cityy/env/sky_dark.tga
		tcMod scroll 0.0025 -0.0075
		rgbGen identityLighting
		tcmod scale 4 4
	}
	{
		map textures/phant_cityy/env/sky_mask.tga
		blendFunc GL_ONE_MINUS_SRC_ALPHA GL_SRC_ALPHA
		tcMod transform 0.25 0 0 0.25 0.1075 0.1075
		rgbGen identityLighting
	}
}
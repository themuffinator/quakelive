textures/ra3fire2/bounce_oldstone4
{
	qer_editorimage textures/mrcleantex_2/bounce_oldstone4.tga
	surfaceparm nodamage
	q3map_lightimage textures/sfx/jumppadsmall.tga	
	q3map_surfacelight 200

	
	{
		map textures/mrcleantex_2/bounce_oldstone4.tga
		rgbGen identity
	}
	
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
	}
	
	{
		map textures/sfx/bouncepad01b_layer1.tga
		blendfunc add
		rgbGen wave sin .5 .5 0 1.5	
	}

	{
		clampmap textures/sfx/jumppadsmall.tga
		blendfunc add
		tcMod stretch sin 1.2 .8 0 1.5
		rgbGen wave square .5 .5 .25 1.5
	}

}

textures/ra3fire2/ra3fire2sky1
{
	qer_editorimage textures/skies/inteldimclouds.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky

	q3map_surfacelight 160
	q3map_lightimage textures/skies/inteldimclouds.tga
	q3map_sun	1 1 0.8 55 30 90

	skyparms - 512 -

	{
		map textures/skies/inteldimclouds.tga
		tcMod scale 3 2
		tcMod scroll 0.15 0.15
		depthWrite
	}
	{
		map textures/skies/topclouds.tga
		blendFunc GL_ONE GL_ONE
		tcMod scale 3 3
		tcMod scroll 0.05 0.05
	}
}

textures/ra3fire2/ra3fire2sky2
{
	qer_editorimage textures/skies/inteldimclouds.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky

	q3map_surfacelight 140
	q3map_lightimage textures/skies/inteldimredclouds.tga
	q3map_sunExt 1 1 0.8 35 30 90 3 16

	skyparms - 512 -

	{
		map textures/skies/inteldimclouds.tga
		tcMod scale 3 2
		tcMod scroll 0.15 0.15
		depthWrite
	}
	{
		map textures/skies/topclouds.tga
		blendFunc GL_ONE GL_ONE
		tcMod scale 3 3
		tcMod scroll 0.05 0.05
	}
}

textures/ra3fire2/ankhlite_wht_1000
{
	qer_editorimage textures/mrcleantex_2/ankhlite_wht.tga
	q3map_surfacelight 1000	
	q3map_lightimage textures/mrcleantex_2/ankhlite_wht.blend.tga	
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/mrcleantex_2/ankhlite_wht.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
	{
		map textures/mrcleantex_2/ankhlite_wht.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}
textures/ra3fire2/ankhlite_wht_2000
{
	qer_editorimage textures/mrcleantex_2/ankhlite_wht.tga
	q3map_surfacelight 2000	
	q3map_lightimage textures/mrcleantex_2/ankhlite_wht.blend.tga	
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/mrcleantex_2/ankhlite_wht.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
	{
		map textures/mrcleantex_2/ankhlite_wht.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}
textures/ra3fire2/ankhlite_wht_3000
{
	qer_editorimage textures/mrcleantex_2/ankhlite_wht.tga
	q3map_surfacelight 3000	
	q3map_lightimage textures/mrcleantex_2/ankhlite_wht.blend.tga	
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/mrcleantex_2/ankhlite_wht.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
	{
		map textures/mrcleantex_2/ankhlite_wht.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}
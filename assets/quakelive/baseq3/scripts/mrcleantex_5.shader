
textures/mrcleantex_5/mrc5_jumppad_blue
{
	qer_editorimage textures/mrcleantex_5/mrc5_jumppad_base.tga
	q3map_lightimage textures/mrcleantex_5/mrc5_jumppad_bluefx.tga	
	q3map_surfacelight 400

        {
			map textures/mrcleantex_5/mrc5_jumppad_bluefx.tga
            rgbGen wave sin .75 .25 0 .5
		}
		{
	        map textures/mrcleantex_4/mrc5_jumppad_base.tga
	        rgbGen identity
		}

        {
			map $lightmap
            blendFunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
			rgbGen identity
	}
}

textures/mrcleantex_5/mrc5_jumppad_orange
{
	surfaceparm nodamage
	qer_editorimage textures/mrcleantex_5/mrc5_jumppad_base.tga
	q3map_lightimage textures/mrcleantex_5/mrc5_jumppad_orangefx.tga	
	q3map_surfacelight 400

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/mrcleantex_5/mrc5_jumppad_base.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity	
	}
	{
		map textures/mrcleantex_5/mrc5_jumppad_orangefx.tga
		blendfunc GL_ONE GL_ONE
		rgbGen wave sin .5 .25 0 .5	
	}

}
textures/mrcleantex_5/mrc5_wastewater
	{
		qer_editorimage textures/mrcleantex_5/mrc5_wastewater.tga
		q3map_lightimage textures/mrcleantex_5/mrc5_wastewater.tga
		q3map_globaltexture
		qer_trans .5

		surfaceparm noimpact
		surfaceparm water
		surfaceparm nolightmap
		surfaceparm trans		

		q3map_surfacelight 100
		tessSize 32
		cull disable

		deformVertexes wave 2 sin 0 .1 .05 .01

		{
			map textures/mrcleantex_5/mrc5_wastewater.tga
			blendfunc GL_DST_COLOR GL_SRC_COLOR
			tcMod turb .01 .01 0 .01
			tcMod scroll .001 .001
		}
		{
			map textures/liquids/pool3d_3.tga
			blendfunc GL_DST_COLOR GL_ONE
			tcMod scale .5 .5
			tcMod scroll -.025 .02
		}

}

textures/mrcleantex_5/mrcq3dm7_sky
{
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky

	qer_editorimage textures/skies/toxicbluesky.tga
	
	q3map_surfacelight 120
//	q3map_sun	.5 .6 .8 150 30 60

	skyparms - 512 -

	{
		map textures/skies/bluedimclouds.tga
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

textures/mrcleantex_5/mrcq3dm7_fog
{
	qer_editorimage textures/mrcleantex_5/mrc5_fog.jpg
	qer_trans 0.4
	surfaceparm fog
	surfaceparm nolightmap
	surfaceparm nonsolid
	surfaceparm trans
	fogparms ( 1.000000 0.644484 0.429405 ) 80000
}

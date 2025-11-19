textures/mrcq3t6/sky1
{
	qer_editorimage textures/skies/intelredclouds.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	q3map_lightsubdivide 256 
	q3map_sun .96 .7 .5 120 60 80
	q3map_lightimage textures/t8dm5/t8sky1.tga
	q3map_surfacelight 90

	skyparms - 512 -
	
	{
		map textures/skies/intelredclouds.tga
		tcMod scroll 0.01 0.01
		tcMod scale 2 2
		depthWrite
	}
	{
		map textures/skies/inteldimclouds.tga
		blendfunc GL_ONE GL_ONE
		tcMod scroll 0.015 0.013
		tcMod scale 1.7 1.4
	}
}
textures/mrcq3t6/mrc_t6_beam
{
        surfaceparm trans	
        surfaceparm nomarks	
        surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	
	{
		map textures/mrcq3t6/mrc_t6_beam.tga
                tcMod Scroll .3 0
                blendFunc add
        }
     
}

textures/mrcq3t6/fireportal
	{
        qer_editorimage textures/sfx/firewalla.tga
	q3map_lightimage textures/sfx/firewalla.tga
	surfaceparm trans	
        surfaceparm nomarks	
        surfaceparm nonsolid
	surfaceparm nolightmap
	q3map_surfacelight 100
        qer_trans .8
	cull none
	{
		map textures/sfx/firewalla.tga
		tcMod Scroll .1 7
                blendFunc add
        }
     	{
		map textures/sfx/firegorre2.tga
		tcMod Scroll -.1 6
                blendFunc blend
        }

}
textures/mrcq3t6/mrc_t6_jp2b
{

	surfaceparm nodamage
	q3map_lightimage textures/mrcq3t6/mrc_t6_jp2b_glow.tga	
	q3map_surfacelight 250
	
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/mrcq3t6/mrc_t6_jp2b.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity	
	}
	{
		map textures/mrcq3t6/mrc_t6_jp2b_glow.tga
		blendfunc GL_ONE GL_ONE
		rgbGen wave sin .5 .5 0 .5	
	}
}
textures/mrcq3t6/mrc_t6_spot_100
{
	qer_editorimage textures/mrcq3t6/mrc_t6_spot.tga
	q3map_lightimage textures/mrcq3t6/mrc_t6_spot_glow.tga
	q3map_surfacelight 100
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/mrcq3t6/mrc_t6_spot.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/mrcq3t6/mrc_t6_spot_glow.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/mrcq3t6/mrc_t6_slight_100
{
	qer_editorimage textures/mrcq3t6/mrc_t6_slight.tga
	q3map_lightimage textures/mrcq3t6/mrc_t6_slight_glow.tga
	q3map_surfacelight 100
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/mrcq3t6/mrc_t6_slight.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/mrcq3t6/mrc_t6_slight_glow.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/mrcq3t6/mrc_t6_slight_1000
{
	qer_editorimage textures/mrcq3t6/mrc_t6_slight.tga
	q3map_lightimage textures/mrcq3t6/mrc_t6_slight_glow.tga
	q3map_surfacelight 1000
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/mrcq3t6/mrc_t6_slight.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/mrcq3t6/mrc_t6_slight_glow.tga
		blendfunc GL_ONE GL_ONE
	}
}
textures/mrcq3t6/mrc_t6_slight_2000
{
	qer_editorimage textures/mrcq3t6/mrc_t6_slight.tga
	q3map_lightimage textures/mrcq3t6/mrc_t6_slight_glow.tga
	q3map_surfacelight 2000
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/mrcq3t6/mrc_t6_slight.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/mrcq3t6/mrc_t6_slight_glow.tga
		blendfunc GL_ONE GL_ONE
	}
}
textures/mrcq3t6/mrc_t6_slight_3000
{
	qer_editorimage textures/mrcq3t6/mrc_t6_slight.tga
	q3map_lightimage textures/mrcq3t6/mrc_t6_slight_glow.tga
	q3map_surfacelight 3000
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/mrcq3t6/mrc_t6_slight.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/mrcq3t6/mrc_t6_slight_glow.tga
		blendfunc GL_ONE GL_ONE
	}
}
textures/mrcq3t6/mrc_t6_slight_4000
{
	qer_editorimage textures/mrcq3t6/mrc_t6_slight.tga
	q3map_lightimage textures/mrcq3t6/mrc_t6_slight_glow.tga
	q3map_surfacelight 4000
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/mrcq3t6/mrc_t6_slight.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/mrcq3t6/mrc_t6_slight_glow.tga
		blendfunc GL_ONE GL_ONE
	}
}

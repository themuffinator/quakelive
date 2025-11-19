textures/ds/ds_portal_sfx
{
	portal
	surfaceparm nolightmap
	{
	
		map textures/common/mirror1.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		depthWrite
	} 
	{
		map textures/common/mirror1.tga
		blendfunc gl_src_alpha gl_one_minus_src_alpha
		depthFunc equal
		alphagen portal 4096
		rgbGen identityLighting	
	}
}

textures/ds/ds-grass1_skybox
{
	qer_editorimage textures/ds/ds-grass1.tga 
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky
	q3map_sunExt .5 .37 .19 100 170 45 3 16
	q3map_surfacelight 100
	skyparms env/ds/ds-grass1 - -
}

textures/ds/ds-grass2_skybox
{
	qer_editorimage textures/ds/ds-grass2.tga 
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky
	q3map_sunExt 1 1 .93 128 315 25 3 16
	q3map_surfacelight 150
	skyparms env/ds/ds-grass2 - -
}

textures/ds/ter_grassdirt
{
    qer_editorimage textures/terrain/qzterra1_dirt1_grass1_ed.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf3/ter_grass2.tga
		rgbGen identity
	}
	{
		map textures/desctf3/ter_mud2.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}
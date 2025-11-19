textures/map_purgatory/asphalt_nonsolid
{
	qer_editorimage textures/ql/asphalt.tga
	surfaceparm nonsolid
	cull none

	{
		map $lightmap
		rgbgen identity
	}
	{
		map textures/ql/asphalt.tga
		blendfunc GL_DST_COLOR GL_SRC_ALPHA
		rgbGen identity
		alphaGen lightingSpecular
	}
}

// smoothed rockwall
textures/map_purgatory/pjrock1_shadeangle_120
{
	qer_editorimage textures/stone/pjrock1.tga
	q3map_nonplanar
	q3map_shadeangle 120
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/stone/pjrock1.tga
		blendFunc filter
	}
}

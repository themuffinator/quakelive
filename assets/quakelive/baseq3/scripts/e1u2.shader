textures/e1u2/light1_4
{
	qer_editorimage textures/e1u2/light1_4.tga
	q3map_lightimage textures/e1u2/light1_4.blend.tga
	surfaceparm nomarks
	q3map_surfacelight 2000
	light 1
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/e1u2/light1_4.tga
		blendfunc GL_DST_COLOR GL_SRC_ALPHA
		rgbGen identity
		alphaGen lightingSpecular
	}
    {
		map textures/e1u2/light1_4.blend.tga
		blendfunc add
	}
}

textures/e1u2/light2_1
{
	qer_editorimage textures/e1u2/light2_1.tga
	q3map_lightimage textures/e1u2/light2_1.blend.tga
	surfaceparm nomarks
	q3map_surfacelight 4000
	light 1
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/e1u2/light2_1.tga
		blendfunc GL_DST_COLOR GL_SRC_ALPHA
		rgbGen identity
		alphaGen lightingSpecular
	}
    {
		map textures/e1u2/light2_1.blend.tga
		blendfunc add
	}
}

textures/e1u2/plate1_5_conveyor
{
	qer_editorimage textures/e1u2/plate1_5.tga
	{
		map textures/e1u2/plate1_5.tga
		tcmod scroll 0 1.5625
	}
	{
		map $lightmap
		blendfunc filter
		rgbgen identity
	}
}

textures/e1u2/suppor1_10
{
	qer_editorimage textures/e1u2/suppor1_10.tga
	q3map_lightimage textures/e1u2/suppor1_10.blend.tga
	surfaceparm nomarks
	q3map_surfacelight 700
	light 1
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/e1u2/suppor1_10.tga
		blendfunc GL_DST_COLOR GL_SRC_ALPHA
		rgbGen identity
		alphaGen lightingSpecular
	}
    {
		map textures/e1u2/suppor1_10.blend.tga
		blendfunc add
	}
}

textures/e1u2/suppor1_14
{
	qer_editorimage textures/e1u2/suppor1_14.tga
	q3map_lightimage textures/e1u2/suppor1_14.blend.tga
	surfaceparm nomarks
	q3map_surfacelight 900
	light 1
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/e1u2/suppor1_14.tga
		blendfunc GL_DST_COLOR GL_SRC_ALPHA
		rgbGen identity
		alphaGen lightingSpecular
	}
    {
		map textures/e1u2/suppor1_14.blend.tga
		blendfunc add
	}
}

textures/e1u2/wslt1_5
{
	qer_editorimage textures/e1u2/wslt1_5.tga
	q3map_lightimage textures/e1u2/wslt1_5.blend.tga
	surfaceparm nomarks
	q3map_surfacelight 1000
	light 1
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/e1u2/wslt1_5.tga
		blendfunc GL_DST_COLOR GL_SRC_ALPHA
		rgbGen identity
		alphaGen lightingSpecular
	}
    {
		map textures/e1u2/wslt1_5.blend.tga
		blendfunc add
	}
}

textures/e1u2/wslt1_6
{
	qer_editorimage textures/e1u2/wslt1_6.tga
	q3map_lightimage textures/e1u2/wslt1_6.blend.tga
	surfaceparm nomarks
	q3map_surfacelight 600
	light 1
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/e1u2/wslt1_6.tga
		blendfunc GL_DST_COLOR GL_SRC_ALPHA
		rgbGen identity
		alphaGen lightingSpecular
	}
    {
		map textures/e1u2/wslt1_6.blend.tga
		blendfunc add
	}
}
textures/tp_ctf/tp_ctf_blue
{
	qer_editorimage textures/tp_ctf/tp_ctf_blue_neon.jpg
	q3map_globaltexture
        surfaceparm nomarks
	q3map_surfacelight 500
    cull disable
	{
        	map textures/tp_ctf/tp_ctf_blue_neon.jpg
    }
 
}

textures/tp_ctf/tp_ctf_red
{
	qer_editorimage textures/tp_ctf/tp_ctf_red_neon.jpg
	q3map_globaltexture
        surfaceparm nomarks
	q3map_surfacelight 500
    cull disable
	{
        	map textures/tp_ctf/tp_ctf_red_neon.jpg
    }
 
}

textures/tp_ctf/window_sky
{
	qer_editorimage textures/tp_ctf/window_sky.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm nodlight
	{
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/tp_ctf/window_sky.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/tp_ctf/PU_spawn
{
	qer_editorimage textures/tp_ctf/snow_tiles_logo.tga
	{
		map textures/tp_ctf/snow_tiles_logo.tga
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc GL_DST_COLOR GL_ZERO
	}
}
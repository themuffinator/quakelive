// Blue translucent texture for the blue directional markers
textures/geit/g_egypt_blue
{
	surfaceparm nolightmap
	surfaceparm nonsolid
	cull twosided
	{
		map textures/geit/g_egypt_blue.tga
		tcGen environment
		blendfunc GL_ONE GL_ONE
	}
}

// Red translucent texture for the red directional markers
textures/geit/g_egypt_red
{
	surfaceparm nolightmap
	surfaceparm nonsolid
	cull twosided
	{
		map textures/geit/g_egypt_red.tga
		tcGen environment
		blendfunc GL_ONE GL_ONE
	}
}

// Grey translucent texture for the neutral directional markers. (redundant)
textures/geit/g_egypt_grey
{
	surfaceparm nolightmap
	surfaceparm nonsolid
	cull twosided
	{
		map textures/geit/g_egypt_grey.tga
		tcGen environment
		blendfunc GL_ONE GL_ONE
	}
}

// Jumppad efect thingy for the blue base
textures/geit/hiero_sfx_blue
{
	qer_editorimage textures/geit/heiro_02_sfx.tga
	surfaceparm nonsolid
	cull twosided
	{
		map textures/geit/heiro_02_sfx.tga
		rgbGen identity
	}
	{
		map textures/sfx/proto_zzztblu3.tga
		tcGen environment
                tcMod turb 0 0.25 0 0.5
                tcmod scroll 1 1
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/geit/g_egypt_beam_yellow.tga
		tcGen environment
                tcmod scroll 0 2
                tcmod scale 0.2 0.2
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/geit/heiro_02_sfx.tga
		blendfunc blend
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
}

// Jumppad efect thingy for the red base
textures/geit/hiero_sfx_red
{
	qer_editorimage textures/geit/heiro_02_sfx.tga
	surfaceparm nonsolid
	cull twosided
	{
		map textures/geit/heiro_02_sfx.tga
		rgbGen identity
	}
	{
		map textures/sfx/proto_zzzt.tga
		tcGen environment
                tcMod turb 0 0.25 0 0.5
                tcmod scroll 1 1
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/geit/g_egypt_beam_yellow.tga
		tcGen environment
                tcmod scroll 0 2
                tcmod scale 0.2 0.2
		blendfunc GL_ONE GL_ONE
	}
	{
		map textures/geit/heiro_02_sfx.tga
		blendfunc blend
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
}

textures/geit/lighttrick_yellow_50
{
	qer_editorimage textures/geit/g_egypt_light_2.tga
	q3map_lightimage textures/geit/g_egypt_light_2.tga

	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_surfacelight 100

	skyparms - - -
	light 1
}

textures/geit/lighttrick_yellow_50_2
{
	qer_editorimage textures/geit/g_egypt_light_2_50.tga
	q3map_lightimage textures/geit/g_egypt_light_2.tga

	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_surfacelight 50

	skyparms - - -
	light 1
}

textures/geit/geit3ctf3_dust
{
	qer_editorimage textures/sfx/hellfog.tga
	qer_trans 0.4
	surfaceparm nonsolid
	surfaceparm nolightmap
	surfaceparm trans
	surfaceparm fog
	fogparms ( .69 .55 .47 ) 1024
}

textures/geit/Spider1
{
	qer_editorimage textures/geit/Spider1.tga
	surfaceparm nonsolid
	surfaceparm noimpact
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nolightmap
	cull disable
	tessSize 256
	deformVertexes wave 256 sin 0 4 0 0.2
	{
		map textures/geit/Spider1.tga
		blendfunc add
		rgbgen identity
	}
}

textures/geit/Spider2
{
	qer_editorimage textures/geit/Spider2.tga
	surfaceparm noimpact
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nolightmap
	cull disable

	{
		map textures/geit/Spider2.tga
		blendfunc add
		rgbgen identity
	}
}
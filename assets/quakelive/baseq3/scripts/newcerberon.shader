textures/ct_1997_ctf/tp_plate_01_red_S
{
	qer_editorimage textures/ct_1997_ctf/tp_plate_01_red.jpg
	q3map_lightimage textures/ct_1997_ctf/tp_plate_01_red.jpg
	surfaceparm nomarks
	{
		map $lightmap 
		rgbGen identity
		tcGen lightmap 
	}
	{
		map textures/ct_1997_ctf/tp_plate_01_red.jpg
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/ct_1997_ctf/tp_plate_01_blend_red.jpg
		blendfunc add
		rgbGen wave sawtooth 0.5 0.5 0 1 
	}
}

textures/ct_1997_ctf/tp_plate_01_blue_S
{
	qer_editorimage textures/ct_1997_ctf/tp_plate_01_red.jpg
	q3map_lightimage textures/ct_1997_ctf/tp_plate_01_red.jpg
	surfaceparm nomarks
	{
		map $lightmap 
		rgbGen identity
		tcGen lightmap 
	}
	{
		map textures/ct_1997_ctf/tp_plate_01_blue.jpg
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/ct_1997_ctf/tp_plate_01_blend_blue.jpg
		blendfunc add
		rgbGen wave sawtooth 0.5 0.5 0 1 
	}
}

//RED TELEPORTER FLARES
textures/ct_1997_ctf/tp_flare_01_red_S
{
	qer_editorimage textures/ct_1997_ctf/tp_flare_01_red.jpg
	surfaceparm nodlight
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nonsolid
	surfaceparm trans
	cull disable
	deformVertexes autosprite
	deformVertexes move 0 0 80 sawtooth 0 1 1 1 
	qer_trans 0.5
	{
		clampmap textures/ct_1997_ctf/tp_flare_01_red.jpg
		blendfunc add
		rgbGen wave sawtooth 1 -1 1 1 
	}
}

textures/ct_1997_ctf/tp_flare_02_red_S
{
	qer_editorimage textures/ct_1997_ctf/tp_flare_01_red.jpg
	surfaceparm nodlight
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nonsolid
	surfaceparm trans
	cull disable
	deformVertexes autosprite
	deformVertexes move 0 0 80 sawtooth 0 1 0.75 1 
	qer_trans 0.5
	{
		clampmap textures/ct_1997_ctf/tp_flare_01_red.jpg
		blendfunc add
		rgbGen wave sawtooth 1 -1 0.75 1 
	}
}

textures/ct_1997_ctf/tp_flare_03_red_S
{
	qer_editorimage textures/ct_1997_ctf/tp_flare_01_red.jpg
	surfaceparm nodlight
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nonsolid
	surfaceparm trans
	cull disable
	deformVertexes autosprite
	deformVertexes move 0 0 80 sawtooth 0 1 0.5 1 
	qer_trans 0.5
	{
		clampmap textures/ct_1997_ctf/tp_flare_01_red.jpg
		blendfunc add
		rgbGen wave sawtooth 1 -1 0.5 1 
	}
}

textures/ct_1997_ctf/tp_flare_04_red_S
{
	qer_editorimage textures/ct_1997_ctf/tp_flare_01_red.jpg
	surfaceparm nodlight
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nonsolid
	surfaceparm trans
	cull disable
	deformVertexes autosprite
	deformVertexes move 0 0 80 sawtooth 0 1 0.25 1 
	qer_trans 0.5
	{
		clampmap textures/ct_1997_ctf/tp_flare_01_red.jpg
		blendfunc add
		rgbGen wave sawtooth 1 -1 0.25 1 
	}
}

//BLUE TELEPORTER FLARES
textures/ct_1997_ctf/tp_flare_01_blue_S
{
	qer_editorimage textures/ct_1997_ctf/tp_flare_01_blue.jpg
	surfaceparm nodlight
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nonsolid
	surfaceparm trans
	cull disable
	deformVertexes autosprite
	deformVertexes move 0 0 80 sawtooth 0 1 1 1 
	qer_trans 0.5
	{
		clampmap textures/ct_1997_ctf/tp_flare_01_blue.jpg
		blendfunc add
		rgbGen wave sawtooth 1 -1 1 1 
	}
}

textures/ct_1997_ctf/tp_flare_02_blue_S
{
	qer_editorimage textures/ct_1997_ctf/tp_flare_01_blue.jpg
	surfaceparm nodlight
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nonsolid
	surfaceparm trans
	cull disable
	deformVertexes autosprite
	deformVertexes move 0 0 80 sawtooth 0 1 0.75 1 
	qer_trans 0.5
	{
		clampmap textures/ct_1997_ctf/tp_flare_01_blue.jpg
		blendfunc add
		rgbGen wave sawtooth 1 -1 0.75 1 
	}
}

textures/ct_1997_ctf/tp_flare_03_blue_S
{
	qer_editorimage textures/ct_1997_ctf/tp_flare_01_blue.jpg
	surfaceparm nodlight
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nonsolid
	surfaceparm trans
	cull disable
	deformVertexes autosprite
	deformVertexes move 0 0 80 sawtooth 0 1 0.5 1 
	qer_trans 0.5
	{
		clampmap textures/ct_1997_ctf/tp_flare_01_blue.jpg
		blendfunc add
		rgbGen wave sawtooth 1 -1 0.5 1 
	}
}

textures/ct_1997_ctf/tp_flare_04_blue_S
{
	qer_editorimage textures/ct_1997_ctf/tp_flare_01_blue.jpg
	surfaceparm nodlight
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nonsolid
	surfaceparm trans
	cull disable
	deformVertexes autosprite
	deformVertexes move 0 0 80 sawtooth 0 1 0.25 1 
	qer_trans 0.5
	{
		clampmap textures/ct_1997_ctf/tp_flare_01_blue.jpg
		blendfunc add
		rgbGen wave sawtooth 1 -1 0.25 1 
	}
}

textures/ct_1997_ctf/screen_01_red_S
{
	qer_editorimage textures/ct_1997_ctf/screen_01_red.jpg
	surfaceparm nomarks
	surfaceparm nonsolid
	cull disable
	nopicmip
	qer_trans 0.4
	{
		map textures/ct_1997_ctf/screen_01_red.jpg
		blendfunc add
		rgbGen wave triangle 0.44 0.12 0 0.8 
	}
	{
		map textures/ct_1997_ctf/screen_01_red.jpg
		blendfunc add
		rgbGen wave triangle 0.05 0.05 1 2.2 
	}
	{
		map textures/ad_content/adbrightoverlay.tga
		blendfunc add
		rgbGen wave sin 0.12 0.05 0 2 
		tcMod scroll 1 0.2
	}
}

textures/ct_1997_ctf/screen_02_red_S
{
	qer_editorimage textures/ct_1997_ctf/screen_02_red.tga
	surfaceparm nomarks
	surfaceparm nonsolid
	cull disable
	nopicmip
	qer_trans 0.4
	{
		map textures/ct_1997_ctf/screen_02_red.tga
		blendfunc add
		rgbGen wave triangle 0.75 0.15 0 0.8 
	}
	{
		map textures/ct_1997_ctf/screen_02.gui_red.tga
		blendfunc add
		rgbGen wave triangle 0.8 0.1 1 1.25 
	}
	{
		clampmap textures/ct_1997_ctf/screen_02.overlay_red.tga
		blendfunc add
		rgbGen wave sin 0.12 0.05 0 2.5 
		alphaFunc GE128
	}
}

textures/ct_1997_ctf/banner_01_blue_S
{
	surfaceparm alphashadow
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm trans
	cull disable
	deformVertexes wave 30 sin 0 2 0 0.2 
	deformVertexes wave 100 sin 0 2 0 0.7 
	tessSize 64
	{
		map textures/ct_1997_ctf/banner_01_blue.tga
		rgbGen identity
		depthWrite
		alphaFunc GE128
	}
	{
		map $lightmap 
		blendfunc filter
		rgbGen identity
		tcGen lightmap 
		depthFunc equal
	}
}

textures/ct_1997_ctf/banner_01_still_blue_S
{
	qer_editorimage textures/ct_1997_ctf/banner_01_blue.tga
	surfaceparm alphashadow
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm trans
	cull disable
	tessSize 64
	{
		map textures/ct_1997_ctf/banner_01_blue.tga
		rgbGen identity
		depthWrite
		alphaFunc GE128
	}
	{
		map $lightmap 
		blendfunc filter
		rgbGen identity
		tcGen lightmap 
		depthFunc equal
	}
}

textures/ct_1997_ctf/patternglass_triangle1
{
	qer_editorimage textures/ct_1997_ctf/patternglass_tri1.jpg
	surfaceparm alphashadow
	surfaceparm nolightmap
	surfaceparm trans
	nopicmip
	sort 7
	{
		map textures/ct_1997_ctf/patternglass_tri1.jpg
		blendfunc filter
	}
	{
		map textures/effects/envmapdimb.tga
		blendfunc add
		tcGen environment 
	}
}

textures/ct_1997_ctf/lightbeam_03_1k
{
	qer_editorimage textures/ct_1997_ctf/lb_beam_03_blend.tga
	q3map_lightimage textures/ct_1997_ctf/lb_beam_03_blend.tga
	surfaceparm nomarks
	q3map_lightsubdivide 32
	q3map_surfacelight 1000
	{
		map $lightmap 
		rgbGen identity
		tcGen lightmap 
	}
	{
		map textures/ct_infinity/lb_beam_01.tga
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/ct_1997_ctf/lb_beam_03_blend.tga
		blendfunc add
	}
}


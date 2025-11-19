textures/desctf3/des_flagred
{
        tessSize 64
        deformVertexes wave 194 sin 0 3 0 .4
        deformVertexes normal .3 .2
	surfaceparm nonsolid
        surfaceparm nomarks
	surfaceparm alphashadow
	qer_trans 0.99
        cull none
        {
		map textures/desctf3/des_flagred.tga
		blendfunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphafunc GT0
		depthwrite
		rgbGen identity
	}

        {
		map $lightmap
                blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
		depthfunc equal
	}
}

textures/desctf3/des_flagblue
{
        tessSize 64
        deformVertexes wave 194 sin 0 3 0 .4
        deformVertexes normal .3 .2
	surfaceparm nonsolid
        surfaceparm nomarks
	surfaceparm alphashadow
	qer_trans 0.99
        cull none
        {
		map textures/desctf3/des_flagblue.tga
		blendfunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphafunc GT0
		depthwrite
		rgbGen identity
	}
        {
		map $lightmap
                blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
		depthfunc equal
	}
}

textures/desctf3/des_gemlight
{
	qer_editorimage textures/desctf3/des_gemlight.jpg
	q3map_lightimage textres/desctf3/des_gemlight_blend.jpg
	q3map_surfacelight 1000
	surfaceparm nodamage
	surfaceparm nonsolid
	surfaceparm trans
	polygonoffset
	sort 6
	{
		map $lightmap
		rgbgen identity
	}
	{
		map textures/desctf3/des_gemlight.jpg
		blendfunc GL_DST_COLOR GL_ZERO
		rgbgen identity
	}
	{
		map textures/desctf3/des_gemlight_blend.jpg
		blendfunc GL_ONE GL_ONE
	}
}

textures/desctf3/des_gemlight_blue
{
	qer_editorimage textures/desctf3/des_gemlight_blue.jpg
	q3map_lightimage textres/desctf3/des_gemlight_blue_blend.jpg
	q3map_surfacelight 1000
	surfaceparm nodamage
	surfaceparm nonsolid
	surfaceparm trans
	polygonoffset
	sort 6
	{
		map $lightmap
		rgbgen identity
	}
	{
		map textures/desctf3/des_gemlight_blue.jpg
		blendfunc GL_DST_COLOR GL_ZERO
		rgbgen identity
	}
	{
		map textures/desctf3/des_gemlight_blue_blend.jpg
		blendfunc GL_ONE GL_ONE
	}
}

textures/desctf3/des_gemlight_red
{
	qer_editorimage textures/desctf3/des_gemlight_red.jpg
	q3map_lightimage textres/desctf3/des_gemlight_red_blend.jpg
	q3map_surfacelight 1000
	surfaceparm nodamage
	surfaceparm nonsolid
	surfaceparm trans
	polygonoffset
	sort 6
	{
		map $lightmap
		rgbgen identity
	}
	{
		map textures/desctf3/des_gemlight_red.jpg
		blendfunc GL_DST_COLOR GL_ZERO
		rgbgen identity
	}
	{
		map textures/desctf3/des_gemlight_red_blend.jpg
		blendfunc GL_ONE GL_ONE
	}
}

textures/desctf3/water
{
	qer_editorimage textures/desctf3/des_water3.tga
	qer_trans 0.99
	q3map_cloneShader textures/desctf3/waterback
	q3map_globaltexture
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm water
	q3map_lightimage textures/desctf3/des_water3.tga
	q3map_surfacelight 10
	//sort 11
	deformvertexes wave 64 sin .5 .5 0 .5
	{
		map textures/desctf3/des_water3.tga
		blendFunc GL_SRC_ALPHA GL_ONE
		depthwrite
		tcmod scale .75 .85
 		tcmod scroll .025 .1
		rgbgen identity
	}
	{
		map textures/desctf3/des_water3.tga
		blendFunc GL_SRC_ALPHA GL_ONE
		depthwrite
		tcmod scale .85 .65
		tcmod scroll -.035 .07
		rgbgen identity
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbgen identity
	}
}

textures/desctf3/water_calm
{
	qer_editorimage textures/desctf3/des_water3.tga
	qer_trans 0.99
	q3map_cloneShader textures/desctf3/waterback
	q3map_globaltexture
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm water
	q3map_lightimage textures/desctf3/des_water3.tga
	q3map_surfacelight 10
	//sort 11
	deformvertexes wave 64 sin .25 .25 0 .5
	{
		map textures/desctf3/des_water3.tga
		blendFunc GL_SRC_ALPHA GL_ONE
		depthwrite
		tcmod scale .5 .5
 		tcmod scroll .025 .01
		rgbgen identity
	}
	{
		map textures/desctf3/des_water3.tga
		blendFunc GL_SRC_ALPHA GL_ONE
		depthwrite
		tcmod scale -.5 -.5
		tcmod scroll .025 .025
		rgbgen identity
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbgen identity
	}
}

textures/desctf3/waterback
{
	qer_editorimage textures/desctf3/des_water3.tga
	qer_trans 0.99
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm water
	surfaceparm nomarks
	q3map_lightimage textures/desctf3/des_water3.tga
	q3map_surfacelight 75
	q3map_globaltexture
	q3map_invert
	q3map_vertexScale .75
	sort 12
	deformvertexes wave 64 sin .5 .5 0 .5
	{
		map textures/desctf3/des_water3.tga
		blendFunc GL_SRC_ALPHA GL_ONE
		depthwrite
		tcmod scale .5 .5
 		tcmod scroll .025 .01
		rgbgen identity
	}
	{
		map textures/desctf3/des_water3.tga
		blendFunc GL_SRC_ALPHA GL_ONE
		depthwrite
		tcmod scale -.5 -.5
		tcmod scroll .025 .025
		rgbgen identity
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbgen identity
	}
}


textures/desctf3/des_watersplash
{
	qer_editorimage textures/desctf3/des_watersplash.tga
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	cull disable
	sort 9
	{
		clampmap textures/desctf3/des_watersplash.tga
		tcmod rotate 10
		tcMod stretch sawtooth 1 0.5 0.25 1.8
		rgbGen wave sin 0.35 0.35 0 1.8	
		blendFunc add
	}
	{
		clampmap textures/desctf3/des_watersplash.tga
		tcmod rotate -8
		tcMod stretch sawtooth 1 0.5 0.55 1.8
		rgbGen wave sin 0.35 0.35 0.3 1.8
		blendFunc add
	}
	{
		clampmap textures/desctf3/des_watersplash.tga
		tcmod rotate 2
		tcMod stretch sawtooth 1 0.5 0.85 1.8
		rgbGen wave sin 0.35 0.35 0.6 1.8
		blendFunc add
	}
}

textures/desctf3/waterfall
{
	qer_editorimage textures/desctf3/waterfall.tga
	qer_trans 0.75
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm noimpact
	surfaceparm nomarks
	q3map_backSplash 25 25
	q3map_surfacelight 30
	cull disable
	sort 12
	deformvertexes wave 192 sin 0 2 0 .5
	{
		map textures/desctf3/waterfall.tga
		blendfunc gl_src_alpha gl_one_minus_src_alpha
		depthwrite
		tcmod scroll 0 -1
		rgbgen identity
		alphagen vertex
	}
}

textures/desctf3/waterfall_nomove
{
	qer_editorimage textures/desctf3/waterfall.tga
	qer_trans 0.75
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm noimpact
	surfaceparm nomarks
	{
		map textures/desctf3/waterfall.tga
		blendfunc gl_src_alpha gl_one_minus_src_alpha
		depthwrite
		tcmod scroll 0 -0.5
		rgbgen identity
		alphagen vertex
	}
}

textures/desctf3/sky
{
	qer_editorimage textures/skies/blacksky.tga
	surfaceparm sky
	surfaceparm nodlight
	surfaceparm noimpact
	surfaceparm nolightmap

	q3map_sunEXT 1 1 1 140 70 75 3 5
	q3map_lightmapFilterRadius 0 8
	q3map_skylight	75 3

	skyparms textures/desctf3/env/sky 1024 -
	nopicmip
	{
		map textures/desctf3/env/clouds.tga
		tcMod scale 1.25 1.25
		tcMod scroll 0.0075 -0.0075
		blendFunc blend
		rgbgen identityLighting
	}	
}

textures/desctf3/des_itemmarker_red
{
	surfaceparm nolightmap
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm trans
	q3map_bounceScale 0

	nopicmip
	polygonOffset
	{
		clampmap textures/desctf3/des_itemmarker_red.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		tcmod rotate -45
		rgbgen wave sin .8 .15 .2 0.05
	}
	{
		clampmap textures/desctf3/des_itemmarker_red.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		tcmod rotate -120
		tcmod stretch sin .75 .1 0 .5
	}
}

textures/desctf3/des_itemmarker_blue
{
	surfaceparm nolightmap
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm trans
	q3map_bounceScale 0

	nopicmip
	polygonOffset
	{
		clampmap textures/desctf3/des_itemmarker_blue.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		tcmod rotate -45
		rgbgen wave sin .8 .15 .2 0.05
	}
	{
		clampmap textures/desctf3/des_itemmarker_blue.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		tcmod rotate -120
		tcmod stretch sin .75 .1 0 .5
	}
}


textures/desctf3/des_stone
{
	q3map_nonplanar
	q3map_shadeangle 100
	
	{
		map textures/desctf3/des_stone.jpg
		rgbGen identity
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf3/des_column
{
	q3map_nonplanar
	q3map_shadeangle 100
	
	{
		map textures/desctf3/des_column.jpg
		rgbGen identity
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf3/des_column2
{
	q3map_nonplanar
	q3map_shadeangle 100
	
	{
		map textures/desctf3/des_column2.jpg
		rgbGen identity
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf3/des_jumppad_blue
{
	qer_editorimage textures/desctf3/des_jumppad.jpg
	surfaceparm trans
	surfaceparm nonsolid	
	surfaceparm nomarks
	surfaceparm nodamage
	{
		map textures/desctf3/des_jumppad.jpg
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map textures/desctf3/des_jumppadfx_blue.jpg
		blendfunc add
		rgbGen wave sin 0 1 0 .8 
	}
}

textures/desctf3/des_jumppadbeam_blue
{
        surfaceparm trans	
        surfaceparm nomarks	
        surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	q3map_surfacelight 200
	sort 10
	{
		map textures/desctf3/des_jumppadbeam_blue.tga
                tcMod Scroll .3 0
                blendFunc add
        }
}

textures/desctf3/des_jumppadfx_blue2
{
	qer_editorimage textures/desctf3/des_jumppadfx_blue2.jpg
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nodamage
	surfaceparm nolightmap
	polygonoffset
	cull none
	sort 9
	deformvertexes move 0 0 15 sawtooth 0 1 0 .8
	{
		map textures/desctf3/des_jumppadfx_blue2.tga
		tcmod rotate 40
		blendfunc add
		rgbgen wave inversesawtooth 0 1 0 .8
	}
	{
		map textures/desctf3/des_jumppadfx_blue2.tga
		tcmod rotate -10
		tcMod stretch sin 1 .25 .5 .8
		blendfunc add
		rgbgen wave inversesawtooth 0 1 0 .8
	}
}

textures/desctf3/des_jumppadfx_blue3
{
	qer_editorimage textures/desctf3/des_jumppadfx_blue3.jpg
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nodamage
	surfaceparm nolightmap
	polygonoffset
	cull none
	sort 9
	deformvertexes move 0 0 30 sawtooth 0 1 0 .8
	{
		clampmap textures/desctf3/des_jumppadfx_blue3.tga
		tcmod rotate 120
		tcMod stretch sawtooth 1 -.5 0 .8
		blendfunc add
		rgbgen wave inversesawtooth 0 1 0 .8
	}
	{
		clampmap textures/desctf3/des_jumppadfx_blue3.tga
		tcmod rotate -60
		tcmod stretch sawtooth 1 -.2 0 .8
		blendfunc add
		rgbgen wave inversesawtooth 0 1 0 .8
	}	
}

textures/desctf3/des_jumppadfx_blue4
{
	qer_editorimage textures/desctf3/des_jumppadfx_blue4.jpg
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nodamage
	surfaceparm nolightmap
	polygonoffset
	cull none
	sort 9
	deformvertexes move 0 0 45 sawtooth 0 1 0 .8
	{
		clampmap textures/desctf3/des_jumppadfx_blue4.tga
		tcmod rotate 120
		tcMod stretch sawtooth 1 -.5 0 .8
		blendfunc add
		rgbgen wave inversesawtooth 0 1 0 .8
	}
}

textures/desctf3/des_jumppad_red
{
	qer_editorimage textures/desctf3/des_jumppad.jpg
	surfaceparm trans
	surfaceparm nonsolid	
	surfaceparm nomarks
	surfaceparm nodamage
	{
		map textures/desctf3/des_jumppad.jpg
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map textures/desctf3/des_jumppadfx_red.jpg
		blendfunc add
		rgbGen wave sin 0 1 0 .8 
	}
}

textures/desctf3/des_jumppadbeam_red
{
        surfaceparm trans	
        surfaceparm nomarks	
        surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	sort 10
	q3map_surfacelight 200
	{
		map textures/desctf3/des_jumppadbeam_red.tga
                tcMod Scroll .3 0
                blendFunc add
        }
}

textures/desctf3/des_jumppadfx_red2
{
	qer_editorimage textures/desctf3/des_jumppadfx_red2.jpg
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nodamage
	surfaceparm nolightmap
	polygonoffset
	cull none
	sort 9
	deformvertexes move 0 0 15 sawtooth 0 1 0 .8
	{
		map textures/desctf3/des_jumppadfx_red2.tga
		tcmod rotate 40
		blendfunc add
		rgbgen wave inversesawtooth 0 1 0 .8
	}
	{
		map textures/desctf3/des_jumppadfx_red2.tga
		tcmod rotate -10
		tcMod stretch sin 1 .25 .5 .8
		blendfunc add
		rgbgen wave inversesawtooth 0 1 0 .8
	}
}

textures/desctf3/des_jumppadfx_red3
{
	qer_editorimage textures/desctf3/des_jumppadfx_red3.jpg
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nodamage
	surfaceparm nolightmap
	polygonoffset
	cull none
	sort 9
	deformvertexes move 0 0 30 sawtooth 0 1 0 .8
	{
		clampmap textures/desctf3/des_jumppadfx_red3.tga
		tcmod rotate 120
		tcMod stretch sawtooth 1 -.5 0 .8
		blendfunc add
		rgbgen wave inversesawtooth 0 1 0 .8
	}
	{
		clampmap textures/desctf3/des_jumppadfx_red3.tga
		tcmod rotate -60
		tcmod stretch sawtooth 1 -.2 0 .8
		blendfunc add
		rgbgen wave inversesawtooth 0 1 0 .8
	}	
}

textures/desctf3/des_jumppadfx_red4
{
	qer_editorimage textures/desctf3/des_jumppadfx_red4.jpg
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nodamage
	surfaceparm nolightmap
	polygonoffset
	cull none
	sort 9
	deformvertexes move 0 0 45 sawtooth 0 1 0 .8
	{
		clampmap textures/desctf3/des_jumppadfx_red4.tga
		tcmod rotate 120
		tcMod stretch sawtooth 1 -.5 0 .8
		blendfunc add
		rgbgen wave inversesawtooth 0 1 0 .8
	}
}

textures/desctf3/ter_rocksand
{
        qer_editorimage textures/desctf3/ter_rocksand.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf3/ter_rock1.tga
		rgbGen identity
	}
	{
		map textures/desctf3/ter_sand1.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphaFunc GT0
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf3/ter_mudsand
{
        qer_editorimage textures/desctf3/ter_mudsand.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf3/ter_mud2.tga
		rgbGen identity
	}
	{
		map textures/desctf3/ter_sand1.tga
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

textures/desctf3/ter_mudgrass
{
        qer_editorimage textures/desctf3/ter_mudgrass.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf3/ter_mud2.tga
		rgbGen identity
	}
	{
		map textures/desctf3/ter_grass2.tga
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

textures/desctf3/ter_grassmoss
{
        qer_editorimage textures/desctf3/ter_grassmoss.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf3/ter_grass2.tga
		rgbGen identity
	}
	{
		map textures/desctf3/ter_moss1.tga
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

textures/desctf3/ter_rockmud
{
	qer_editorimage textures/desctf3/ter_rockmud.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	
	{
		map textures/desctf3/ter_rock1.tga
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

textures/desctf3/ter_dirtmud
{
        qer_editorimage textures/desctf3/ter_dirtmud.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf3/ter_dirt1.tga
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

textures/desctf3/ter_dirtsand
{
        qer_editorimage textures/desctf3/ter_dirtsand.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf3/ter_dirt1.tga
		rgbGen identity
	}
	{
		map textures/desctf3/ter_sand1.tga
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

textures/desctf3/ter_dirtmoss
{
        qer_editorimage textures/desctf3/ter_dirtmoss.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf3/ter_dirt1.tga
		rgbGen identity
	}
	{
		map textures/desctf3/ter_moss1.tga
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

textures/desctf3/ter_mossmud
{
        qer_editorimage textures/desctf3/ter_mossmud.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	
	{
		map textures/desctf3/ter_moss1.tga
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

textures/desctf3/ter_rockmoss
{
        qer_editorimage textures/desctf3/ter_rockmoss.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf3/ter_rock4.tga
		rgbGen identity
	}
	{
		map textures/desctf3/ter_moss1.tga
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


textures/desctf3/ter_dirtgravel
{
        qer_editorimage textures/desctf3/ter_dirtgravel.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	
	{
		map textures/desctf3/ter_dirt1.tga
		rgbGen identity
	}
	{
		map textures/desctf3/ter_gravel1.tga
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


textures/desctf3/ter_rock1
{
	qer_editorimage textures/desctf3/ter_rock1.tga

	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/desctf3/ter_rock1.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}


textures/desctf3/ter_moss1
{
	qer_editorimage textures/desctf3/ter_moss1.tga

	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/desctf3/ter_moss1.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf3/ter_sand1
{
	qer_editorimage textures/desctf3/ter_sand1.tga

	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/desctf3/ter_sand1.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}


textures/desctf3/bld_rock2sand
{
	qer_editorimage textures/desctf3/ter_sand1.tga

	q3map_nonplanar
	q3map_shadeAngle 135
	q3map_alphaMod dotproduct2 ( 0 0 .95 )
	{
		map textures/desctf3/ter_rock1.tga
		rgbGen identity
	}
	{
		map textures/desctf3/ter_sand1.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphaFunc GT0
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}

}

textures/desctf3/bld_rock2moss
{
	qer_editorimage textures/desctf3/ter_moss1.tga

	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map textures/desctf3/ter_rock1.tga
		rgbGen identity
	}
	{
		map textures/desctf3/ter_moss1.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphaFunc GT0
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}
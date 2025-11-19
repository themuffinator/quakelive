textures/desctf5/sky
{
	qer_editorimage textures/skies/blacksky.tga
	surfaceparm sky
	surfaceparm nodlight
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_sunEXT .78 .88 1 65 70 90 3 5
	q3map_lightmapFilterRadius 0 8
	q3map_skylight	65 3
	skyparms textures/desctf5/env/sky 1024 -
	{
		map textures/desctf5/env/mask.tga
		blendFunc GL_ONE_MINUS_SRC_ALPHA GL_SRC_ALPHA
		tcMod transform 0.25 0 0 0.25 0.1075 0.1075
		rgbGen identityLighting
	}
}

textures/desctf5/fog
{
	qer_editorimage textures/common/black.tga
	qer_trans .5
	surfaceparm	trans
	surfaceparm	nonsolid
	surfaceparm	fog
	surfaceparm	nolightmap
	qer_nocarve
	fogparms ( 0 0 0 ) 2500
}

textures/desctf5/bld_rock2fog
{
	qer_editorimage textures/desctf5/ter_rock1.tga
	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/desctf5/ter_rock1.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/common/black.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identityLighting
		alphaGen Vertex
	}
}

textures/desctf5/des_banner_red
{
    tessSize 64
    deformVertexes wave 194 sin 0 3 0 .4
    deformVertexes normal .3 .2
	surfaceparm nonsolid
    surfaceparm nomarks
    cull none
    {
		map textures/desctf5/des_banner_red.tga
		rgbGen identity
	}
    {
		map $lightmap
        blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf5/des_banner_blue
{
    tessSize 64
    deformVertexes wave 194 sin 0 3 0 .4
    deformVertexes normal .3 .2
	surfaceparm nonsolid
    surfaceparm nomarks
    cull none
    {
		map textures/desctf5/des_banner_blue.tga
		rgbGen identity
	}
    {
		map $lightmap
        blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf5/des_lantern_blue
{
	surfaceparm nomarks
	surfaceparm lightfilter
	q3map_lightmapFilterRadius 0 4
	q3map_surfacelight 500
	q3map_lightimage textures/desctf5/des_lantern_blend.tga
	qer_editorimage textures/desctf5/des_lantern_blue.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/desctf5/des_lantern_blend.tga
		blendFunc GL_ONE GL_ONE
		rgbGen identity
	}
	{
		map textures/desctf5/des_lantern_blue.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf5/des_lantern_red
{
	surfaceparm nomarks	surfaceparm lightfilter
	q3map_lightmapFilterRadius 0 4
	q3map_surfacelight 500
	q3map_lightimage textures/desctf5/des_lantern_blend.tga
	qer_editorimage textures/desctf5/des_lantern_red.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/desctf5/des_lantern_blend.tga
		blendFunc GL_ONE GL_ONE
		rgbGen identity
	}
	{
		map textures/desctf5/des_lantern_red.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf5/des_lantern_glass
{
	surfaceparm nomarks
	q3map_surfacelight 500
	q3map_lightimage textures/desctf5/des_lantern_glass_blend.tga
	qer_editorimage textures/desctf5/des_lantern_glass.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/desctf5/des_lantern_glass_blend.tga
		blendFunc GL_ONE GL_ONE
		rgbGen identity
	}
	{
		map textures/desctf5/des_lantern_glass.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf5/des_paperwall
{
	qer_editorimage textures/desctf5/des_paperwall.tga
	cull none
	{
		map textures/desctf5/des_paperwall.tga
		rgbGen identity
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf5/des_wicker
{
	qer_editorimage textures/desctf5/des_wicker.tga
	cull none
	{
		map textures/desctf5/des_wicker.tga
		rgbGen identity
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf5/des_gold_round
{
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm alphashadow
	q3map_vertexScale 0.75
	polygonoffset
	sort 6
	{
		map textures/desctf5/des_gold_round.tga
		blendfunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbgen identity
		depthfunc equal
	}
}

textures/desctf5/des_gold_trim
{
	{
		map textures/effects/tinfx.tga
		tcGen environment
		rgbGen identity
	}
	{
		map textures/desctf5/des_gold_trim.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
	}
	{
		map $lightmap
		blendFunc filter //GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
}

textures/desctf5/des_woodtile
{
	qer_editorimage textures/desctf5/des_woodtile.tga
	surfaceparm	woodsteps
	{
		map $lightmap
		rgbGen identity	
	}
	{
		map textures/desctf5/des_woodtile.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/desctf5/des_woodplanks
{
	qer_editorimage textures/desctf5/des_woodplanks.tga
	surfaceparm 	woodsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/desctf5/des_woodplanks.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/desctf5/des_moss_decal
{
	qer_trans .99
	polygonOffset
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm trans
	q3map_bounceScale 0
	{
		map textures/desctf5/des_moss_decal.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
	}
}

textures/desctf5/des_jumppad_blue
{
	qer_editorimage textures/desctf5/des_jumppad_blue.jpg
	q3map_cloneshader textures/desctf5/des_jumppad_bluefx1
	surfaceparm trans
	surfaceparm nonsolid	
	surfaceparm nomarks
	surfaceparm nodamage
	q3map_lightImage textures/desctf5/des_jumppad_blue_glow.tga
	q3map_surfacelight 200
	{
		map textures/desctf5/des_jumppad_blue.jpg
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map textures/desctf5/des_jumppad_blue_glow.jpg
		blendfunc add
		rgbGen wave inversesawtooth 0 1 0 .8 
	}
}

textures/desctf5/des_jumppad_bluefx1
{
	q3map_cloneshader textures/desctf5/des_jumppad_bluefx2
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm nolightmap
	surfaceparm nodamage
	polygonoffset
	cull none
	deformvertexes move 0 0 15 sawtooth 0 1 0 .8
	{
		clampmap textures/desctf5/des_jumppad_blue_glow.jpg
		blendfunc add
		tcMod stretch sawtooth 1 -.25 0 .8 
		rgbgen wave inversesawtooth 0 .5 0 .8
	}
}

textures/desctf5/des_jumppad_bluefx2
{
	q3map_cloneshader textures/desctf5/des_jumppad_bluefx3
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm nolightmap
	surfaceparm nodamage
	polygonoffset
	cull none
	deformvertexes move 0 0 30 sawtooth 0 1 0 .8
	{
		clampmap textures/desctf5/des_jumppad_blue_glow.jpg
		blendfunc add
		tcMod stretch sawtooth 1 -.5 0 .8
		rgbgen wave inversesawtooth 0 .75 0 .8
	}
}

textures/desctf5/des_jumppad_bluefx3
{
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm nolightmap
	surfaceparm nodamage
	polygonoffset
	cull none
	deformvertexes move 0 0 45 sawtooth 0 1 0 .8
	{
		clampmap textures/desctf5/des_jumppad_blue_glow.jpg
		blendfunc add
		tcMod stretch sawtooth 1 -.75 0 .8
		rgbgen wave inversesawtooth 0 1 0 .8
	}
}

textures/desctf5/des_jumppad_red
{
	qer_editorimage textures/desctf5/des_jumppad_red.jpg
	q3map_cloneshader textures/desctf5/des_jumppad_redfx1
	surfaceparm trans
	surfaceparm nonsolid	
	surfaceparm nomarks
	surfaceparm nodamage
	q3map_lightImage textures/desctf5/des_jumppad_red_glow.tga
	q3map_surfacelight 200
	{
		map textures/desctf5/des_jumppad_red.jpg
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map textures/desctf5/des_jumppad_red_glow.jpg
		blendfunc add
		rgbGen wave inversesawtooth 0 1 0 .8 
	}
}

textures/desctf5/des_jumppad_redfx1
{
	q3map_cloneshader textures/desctf5/des_jumppad_redfx2
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm nolightmap
	surfaceparm nodamage
	polygonoffset
	cull none
	deformvertexes move 0 0 15 sawtooth 0 1 0 .8
	{
		clampmap textures/desctf5/des_jumppad_red_glow.jpg
		blendfunc add
		tcMod stretch sawtooth 1 -.25 0 .8
		rgbgen wave inversesawtooth 0 .5 0 .8
	}
}

textures/desctf5/des_jumppad_redfx2
{
	q3map_cloneshader textures/desctf5/des_jumppad_redfx3
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm nolightmap
	surfaceparm nodamage
	polygonoffset
	cull none
	deformvertexes move 0 0 30 sawtooth 0 1 0 .8
	{
		clampmap textures/desctf5/des_jumppad_red_glow.jpg
		blendfunc add
		tcMod stretch sawtooth 1 -.5 0 .8
		rgbgen wave inversesawtooth 0 .75 0 .8
	}
}

textures/desctf5/des_jumppad_redfx3
{
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm nolightmap
	surfaceparm nodamage
	polygonoffset
	cull none
	deformvertexes move 0 0 45 sawtooth 0 1 0 .8
	{
		clampmap textures/desctf5/des_jumppad_red_glow.jpg
		blendfunc add
		tcMod stretch sawtooth 1 -.75 0 .8
		rgbgen wave inversesawtooth 0 1 0 .8
	}
}

textures/desctf5/des_watersplash
{
	qer_editorimage textures/desctf5/des_watersplash.tga
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	cull disable
	sort 10
	{
		clampmap textures/desctf5/des_watersplash.tga
		tcmod rotate 10
		tcMod stretch sawtooth 1 0.5 0.25 1.8
		rgbGen wave sin 0.35 0.35 0 1.8	
		blendFunc add
	}
	{
		clampmap textures/desctf5/des_watersplash.tga
		tcmod rotate -8
		tcMod stretch sawtooth 1 0.5 0.55 1.8
		rgbGen wave sin 0.35 0.35 0.3 1.8
		blendFunc add
	}
	{
		clampmap textures/desctf5/des_watersplash.tga
		tcmod rotate 2
		tcMod stretch sawtooth 1 0.5 0.85 1.8
		rgbGen wave sin 0.35 0.35 0.6 1.8
		blendFunc add
	}
}

textures/desctf5/waterfall
{
	qer_editorimage textures/desctf5/waterfall.tga
	qer_trans 0.75
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm noimpact
	surfaceparm nomarks
	q3map_backSplash 25 25
	q3map_surfacelight 50
	cull disable
	sort 11
	deformvertexes wave 192 sin 0 2 0 .5
	{
		map textures/desctf5/waterfall.tga
		blendfunc gl_src_alpha gl_one_minus_src_alpha
		depthwrite
		tcmod scroll 0 -1
		rgbgen identity
		alphagen vertex
	}
}

textures/desctf5/des_rock_smooth
{
	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/desctf5/des_rock_smooth.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf5/ter_rocksand
{
    qer_editorimage textures/desctf5/ter_rocksand.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf5/ter_rock1.tga	// Primary
		rgbGen identity
	}
	{
		map textures/desctf5/ter_sand1.tga	// Secondary
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

textures/desctf5/ter_mudsand
{
    qer_editorimage textures/desctf5/ter_mudsand.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf5/ter_mud2.tga	// Primary
		rgbGen identity
	}
	{
		map textures/desctf5/ter_sand1.tga	// Secondary
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

textures/desctf5/ter_mudgrass
{
    qer_editorimage textures/desctf5/ter_mudgrass.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf5/ter_mud2.tga	// Primary
		rgbGen identity
	}
	{
		map textures/desctf5/ter_grass2.tga	// Secondary
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

textures/desctf5/ter_grassmoss
{
    qer_editorimage textures/desctf5/ter_grassmoss.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf5/ter_grass2.tga	// Primary
		rgbGen identity
	}
	{
		map textures/desctf5/ter_moss1.tga	// Secondary
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

textures/desctf5/ter_mossmud
{
	qer_editorimage textures/desctf5/ter_mossmud.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf5/ter_moss1.tga
		rgbGen identity
	}
	{
		map textures/desctf5/ter_mud2.tga
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

textures/desctf5/ter_rockmud
{
	qer_editorimage textures/desctf5/ter_rockmud.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	
	{
		map textures/desctf5/ter_rock1.tga	// Primary
		rgbGen identity
	}
	{
		map textures/desctf5/ter_mud2.tga	// Secondary
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

textures/desctf5/ter_rockalgae
{
	qer_editorimage textures/desctf5/ter_rockalgae.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf5/ter_rock1.tga
		rgbGen identity
	}
	{
		map textures/desctf5/ter_algae2.tga
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

textures/desctf5/ter_dirtmud
{
    qer_editorimage textures/desctf5/ter_dirtmud.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/desctf5/ter_dirt1.tga	// Primary
		rgbGen identity
	}
	{
		map textures/desctf5/ter_mud2.tga	// Secondary
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

textures/desctf5/ter_rock1
{
	qer_editorimage textures/desctf5/ter_rock1.tga
	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/desctf5/ter_rock1.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf5/ter_moss1
{
	qer_editorimage textures/desctf5/ter_moss1.tga
	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/desctf5/ter_moss1.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf5/ter_sand1
{
	qer_editorimage textures/desctf5/ter_sand1.tga
	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/desctf5/ter_sand1.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf5/bld_rock2sand
{
	qer_editorimage textures/desctf5/ter_sand1.tga
	q3map_nonplanar
	q3map_shadeAngle 135
	q3map_alphaMod dotproduct2 ( 0 0 .95 )
	{
		map textures/desctf5/ter_rock1.tga
		rgbGen identity
	}
	{
		map textures/desctf5/ter_sand1.tga
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

textures/desctf5/bld_rock2algae
{
	qer_editorimage textures/desctf5/ter_algae1.tga
	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map textures/desctf5/ter_rock1.tga
		rgbgen identity
	}
	{
		map textures/desctf5/ter_algae1.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphaFunc GT0
		rgbgen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/desctf5/bld_rock2moss
{
	qer_editorimage textures/desctf5/ter_moss1.tga
	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map textures/desctf5/ter_rock1.tga
		rgbGen identity
	}
	{
		map textures/desctf5/ter_moss1.tga
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

textures/desctf5/bld_rock2cliff
{
	qer_editorimage textures/desctf5/ter_rock1.tga
	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map textures/desctf5/ter_cliff1.tga
		rgbGen identity
	}
	{
		map textures/desctf5/ter_rock1.tga
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
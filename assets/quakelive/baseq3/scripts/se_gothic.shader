textures/se_gothic/brick_01
{
	qer_editorimage textures/se_gothic/brick_01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/brick_01.tga
		blendfunc filter
	}
}

textures/se_gothic/brick_02
{
	qer_editorimage textures/se_gothic/brick_02.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/brick_02.tga
		blendfunc filter
	}
}

textures/se_gothic/brick_03
{
	qer_editorimage textures/se_gothic/brick_03.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/brick_03.tga
		blendfunc filter
	}
}

textures/se_gothic/brick_03_sectional
{
	qer_editorimage textures/se_gothic/brick_03_sectional.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/brick_03_sectional.tga
		blendfunc filter
	}
}

textures/se_gothic/brick_03_talltrimmed
{
	qer_editorimage textures/se_gothic/brick_03_talltrimmed.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/brick_03_talltrimmed.tga
		blendfunc filter
	}
}

textures/se_gothic/brick_04
{
	qer_editorimage textures/se_gothic/brick_04.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/brick_04.tga
		tcmod scale 2 2
		blendfunc filter
	}
}

textures/se_gothic/cobblestone_01
{
	qer_editorimage textures/se_gothic/cobblestone_01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/cobblestone_01.tga
		tcmod scale 2 2
		blendfunc filter
	}
}

textures/se_gothic/cobblestone_02
{
	qer_editorimage textures/se_gothic/cobblestone_02.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/cobblestone_02.tga
		tcmod scale 2 2
		blendfunc filter
	}
}

textures/se_gothic/cobblestone_03
{
	qer_editorimage textures/se_gothic/cobblestone_03.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/cobblestone_03.tga
		tcmod scale 2 2
		blendfunc filter
	}
}

textures/se_gothic/cobweb_01
{
	qer_editorimage textures/se_gothic/cobweb_01.tga
	qer_trans 0.8
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	cull none
	nopicmip
	deformVertexes wave 10 sin 0 2 0 0.2

	{
		map textures/se_gothic/cobweb_01.tga
		blendfunc add
	}
}

textures/se_gothic/fam_credits
{
	surfaceparm	nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/fam_credits.tga
		blendfunc filter
	}
}

textures/se_gothic/flame_4_2k
{
	qer_editorimage textures/sfx/flame1.tga
	q3map_lightimage textures/se_gothic/flame.lightimage.tga
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm trans
	cull none
	q3map_surfacelight 2000
	nopicmip
	{
		animMap 10 textures/sfx/flame1.tga textures/sfx/flame2.tga textures/sfx/flame3.tga textures/sfx/flame4.tga textures/sfx/flame5.tga textures/sfx/flame6.tga textures/sfx/flame7.tga textures/sfx/flame8.tga
		blendfunc add
		rgbGen wave inverseSawtooth 0 1 0 10
		
	}	
	{
		animMap 10 textures/sfx/flame2.tga textures/sfx/flame3.tga textures/sfx/flame4.tga textures/sfx/flame5.tga textures/sfx/flame6.tga textures/sfx/flame7.tga textures/sfx/flame8.tga textures/sfx/flame1.tga
		blendfunc add
		rgbGen wave sawtooth 0 1 0 10
	}	
	{
		map textures/sfx/flameball.tga
		blendfunc add
		rgbGen wave sin .6 .2 0 .6	
	}
}

textures/se_gothic/flame_4_4k
{
	qer_editorimage textures/sfx/flame1.tga
	q3map_lightimage textures/se_gothic/flame.lightimage.tga
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm trans
	cull none
	q3map_surfacelight 4000
	nopicmip
	{
		animMap 10 textures/sfx/flame1.tga textures/sfx/flame2.tga textures/sfx/flame3.tga textures/sfx/flame4.tga textures/sfx/flame5.tga textures/sfx/flame6.tga textures/sfx/flame7.tga textures/sfx/flame8.tga
		blendfunc add
		rgbGen wave inverseSawtooth 0 1 0 10
		
	}	
	{
		animMap 10 textures/sfx/flame2.tga textures/sfx/flame3.tga textures/sfx/flame4.tga textures/sfx/flame5.tga textures/sfx/flame6.tga textures/sfx/flame7.tga textures/sfx/flame8.tga textures/sfx/flame1.tga
		blendfunc add
		rgbGen wave sawtooth 0 1 0 10
	}	
	{
		map textures/sfx/flameball.tga
		blendfunc add
		rgbGen wave sin .6 .2 0 .6	
	}
}

textures/se_gothic/flame_4_8k
{
	qer_editorimage textures/sfx/flame1.tga
	q3map_lightimage textures/se_gothic/flame.lightimage.tga
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm trans
	cull none
	q3map_surfacelight 8000
	nopicmip
	{
		animMap 10 textures/sfx/flame1.tga textures/sfx/flame2.tga textures/sfx/flame3.tga textures/sfx/flame4.tga textures/sfx/flame5.tga textures/sfx/flame6.tga textures/sfx/flame7.tga textures/sfx/flame8.tga
		blendfunc add
		rgbGen wave inverseSawtooth 0 1 0 10
		
	}	
	{
		animMap 10 textures/sfx/flame2.tga textures/sfx/flame3.tga textures/sfx/flame4.tga textures/sfx/flame5.tga textures/sfx/flame6.tga textures/sfx/flame7.tga textures/sfx/flame8.tga textures/sfx/flame1.tga
		blendfunc add
		rgbGen wave sawtooth 0 1 0 10
	}	
	{
		map textures/sfx/flameball.tga
		blendfunc add
		rgbGen wave sin .6 .2 0 .6	
	}
}

textures/se_gothic/flame_4_10k
{
	qer_editorimage textures/sfx/flame1.tga
	q3map_lightimage textures/se_gothic/flame.lightimage.tga
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm trans
	cull none
	q3map_surfacelight 10000
	nopicmip
	{
		animMap 10 textures/sfx/flame1.tga textures/sfx/flame2.tga textures/sfx/flame3.tga textures/sfx/flame4.tga textures/sfx/flame5.tga textures/sfx/flame6.tga textures/sfx/flame7.tga textures/sfx/flame8.tga
		blendfunc add
		rgbGen wave inverseSawtooth 0 1 0 10
		
	}	
	{
		animMap 10 textures/sfx/flame2.tga textures/sfx/flame3.tga textures/sfx/flame4.tga textures/sfx/flame5.tga textures/sfx/flame6.tga textures/sfx/flame7.tga textures/sfx/flame8.tga textures/sfx/flame1.tga
		blendfunc add
		rgbGen wave sawtooth 0 1 0 10
	}	
	{
		map textures/sfx/flameball.tga
		blendfunc add
		rgbGen wave sin .6 .2 0 .6	
	}
}

textures/se_gothic/grate_01
{
	surfaceparm trans		
	surfaceparm nonsolid
	surfaceparm	metalsteps
	surfaceparm alphashadow
	surfaceparm playerclip
	surfaceparm nomarks
	cull none
    nopicmip
	{
		map textures/se_gothic/grate_01.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap 
		blendfunc filter
		rgbGen identity
		tcGen lightmap 
		depthFunc equal
	}
}

textures/se_gothic/grate_02
{
	surfaceparm trans		
	surfaceparm nonsolid
	surfaceparm	metalsteps
	surfaceparm alphashadow
	surfaceparm playerclip
	surfaceparm nomarks
	cull none
    nopicmip
	{
		map textures/se_gothic/grate_02.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap 
		blendfunc filter
		rgbGen identity
		tcGen lightmap 
		depthFunc equal
	}
}

textures/se_gothic/ground
{
	q3map_shadeangle 60
	surfaceparm dust
	{
 		map $lightmap
 		rgbGen identity
 	}
 	{
 		map textures/se_gothic/ground.tga
 		blendfunc filter
		tcmod scale 2 2
 	}
}

textures/se_gothic/ground2
{
	q3map_shadeangle 60
	{
 		map $lightmap
 		rgbGen identity
 	}
 	{
 		map textures/se_gothic/ground2.tga
 		blendfunc filter
		tcmod scale 2 2
 	}
}

textures/se_gothic/item_01
{
	qer_editorimage textures/se_gothic/item_01.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	polygonOffset
	sort 6
	{
		map textures/se_gothic/item_01.tga
		blendfunc add
	}
}

textures/se_gothic/item_decal_armor
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_armor.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_armor.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_armor_blue
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_armor_blue.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_armor.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_armor_red
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_armor_red.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_armor.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_bs
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_bs.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_bs.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_bs_blue
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_bs_blue.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_bs.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_bs_red
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_bs_red.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_bs.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_gl
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_gl.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_gl.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_gl_blue
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_gl_blue.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_gl.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_gl_red
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_gl_red.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_gl.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_lg
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_lg.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_lg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_lg_blue
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_lg_blue.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_lg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_lg_red
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_lg_red.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_lg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_mh
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_mh.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_mh.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_mh_blue
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_mh_blue.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_mh.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_mh_red
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_mh_red.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_mh.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_ng_blue
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_ng_blue.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_ng.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_ng_red
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_ng_red.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_ng.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_pg
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_pg.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_pg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_pg_blue
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_pg_blue.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_pg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_pg_red
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_pg_red.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_pg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_hmg
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_hmg.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_hmg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_hmg_blue
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_hmg_blue.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_hmg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_hmg_red
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_hmg_red.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_hmg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_hmg_sand
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_hmg_sand.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_hmg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_regen
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_regen.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_regen.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_regen_blue
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_regen_blue.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_regen.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_regen_red
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_regen_red.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_regen.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_rg
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_rg.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_rg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_rg_blue
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_rg_blue.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_rg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_rg_red
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_rg_red.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_rg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_rl
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_rl.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_rl.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_rl_blue
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_rl_blue.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_rl.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_rl_red
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_rl_red.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_rl.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_quad
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_quad.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_quad.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_quad_blue
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_quad_blue.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_quad.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_quad_red
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_quad_red.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_quad.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_sg
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_sg.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_sg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_sg_blue
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_sg_blue.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_sg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/item_decal_sg_red
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/item_decal_sg_red.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_sg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/light_01_vented
{
	qer_editorimage textures/se_gothic/light_01_vented.tga
	q3map_lightimage textures/se_gothic/light_01_vented.blend.tga
	surfaceparm nomarks
	q3map_surfacelight 400
	{
		map $lightmap 
		rgbGen identity
		tcGen lightmap 
	}
	{
		map textures/se_gothic/light_01_vented.tga
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/se_gothic/light_01_vented.blend.tga
		blendfunc add
		rgbGen identity
	}
}

textures/se_gothic/light_02
{
	qer_editorimage textures/se_gothic/light_02.tga
	q3map_lightimage textures/se_gothic/light_02.blend.tga
	surfaceparm nomarks
	q3map_surfacelight 700
	{
		map $lightmap 
		rgbGen identity
		tcGen lightmap 
	}
	{
		map textures/se_gothic/light_02.tga
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/se_gothic/light_02.blend.tga
		blendfunc add
		rgbGen identity
	}
}

textures/se_gothic/light_03
{
	qer_editorimage textures/se_gothic/light_03.tga
	q3map_lightimage textures/se_gothic/light_03.blend.tga
	surfaceparm nomarks
	q3map_surfacelight 700
	{
		map $lightmap 
		rgbGen identity
		tcGen lightmap 
	}
	{
		map textures/se_gothic/light_03.tga
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/se_gothic/light_03.blend.tga
		blendfunc add
		rgbGen identity
	}
}

textures/se_gothic/metal_01
{
	qer_editorimage textures/se_gothic/metal_01.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/metal_01.tga
		blendfunc filter
	}
}

textures/se_gothic/metalsupport_01
{
	qer_editorimage textures/se_gothic/metalsupport_01.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/metalsupport_01.tga
		blendfunc filter
	}
}

textures/se_gothic/metalsupport_02
{
	qer_editorimage textures/se_gothic/metalsupport_02.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/metalsupport_02.tga
		blendfunc filter
	}
}

textures/se_gothic/metalsupport_03
{
	qer_editorimage textures/se_gothic/metalsupport_03.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/metalsupport_03.tga
		blendfunc filter
	}
}

textures/se_gothic/metalsupport_03_blue
{
	qer_editorimage textures/se_gothic/metalsupport_03_blue.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/metalsupport_03_blue.tga
		blendfunc filter
	}
}

textures/se_gothic/metalsupport_03_red
{
	qer_editorimage textures/se_gothic/metalsupport_03_red.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/metalsupport_03_red.tga
		blendfunc filter
	}
}

textures/se_gothic/not_invis
{
	qer_editorimage textures/se_gothic/not_invis.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	polygonOffset
	sort 6
	qer_trans .75
	{
		map textures/se_gothic/not_invis.tga
		blendfunc add
	}
}

textures/se_gothic/obelisk
{
	qer_editorimage textures/se_gothic/green_dust.tga
	surfaceparm nolightmap
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
   {
		// Pre-pulse buildup
		map textures/se_gothic/green_dust.tga
		blendfunc add
		rgbGen wave sin 0.25 0.1 0 0.5
		tcMod scale 1 0.75
		tcMod scroll 0.25 0
	}
	{
		map textures/se_gothic/runes.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		tcMod scale 1 1.5
		tcMod Scroll -0.2 -0.25
	}
	{
		map textures/se_gothic/runes_motion.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		rgbGen wave square 0.25 0.2 0.5 2
		tcMod scale 1 0.5
		tcMod scroll -0.1 -0.65
		detail
	}	
}

textures/se_gothic/plate_01
{
	qer_editorimage textures/se_gothic/plate_01.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/plate_01.tga
		blendfunc filter
	}
}

textures/se_gothic/plate_gold
{
	qer_editorimage textures/se_gothic/plate_gold.tga
	surfaceparm	metalsteps
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/plate_gold.tga
		blendfunc filter
	}
}

textures/se_gothic/plate_gold_shiny
{
	qer_editorimage textures/se_gothic/plate_gold.tga
	surfaceparm	metalsteps
	nopicmip
	{
		map textures/effects/copperfx.tga       
		tcGen environment
		rgbGen identity
	} 
	{
		map textures/se_gothic/plate_gold.tga
		blendfunc blend
		rgbGen identity
	} 
	{
		map $lightmap
		blendfunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
}

textures/se_gothic/plate_silver
{
	qer_editorimage textures/se_gothic/plate_silver.tga
	surfaceparm	metalsteps
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/plate_silver.tga
		blendfunc filter
	}
}

textures/se_gothic/plate_silver_shiny
{
	qer_editorimage textures/se_gothic/plate_silver.tga
	surfaceparm	metalsteps
	nopicmip
	{
		map textures/effects/tinfx.tga       
		tcGen environment
		rgbGen identity
	} 
	{
		map textures/se_gothic/plate_silver.tga
		blendfunc blend
		rgbGen identity
	} 
	{
		map $lightmap
		blendfunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
}

textures/se_gothic/repent_banner_01
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
	 surfaceparm nonsolid
     tessSize 64
     deformVertexes wave 30 sin 0 2 0 .2
     deformVertexes wave 100 sin 0 2 0 .7
	{
        map textures/se_gothic/repent_banner_01.tga
        alphaFunc GE128
		depthWrite
		rgbGen identity
    }
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

textures/se_gothic/repent_banner_02
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
	 surfaceparm nonsolid
     tessSize 64
     deformVertexes wave 30 sin 0 2 0 .2
     deformVertexes wave 100 sin 0 2 0 .7
	{
        map textures/se_gothic/repent_banner_02.tga
        alphaFunc GE128
		depthWrite
		rgbGen identity
    }
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

textures/se_gothic/repent_cathedral_tower_window
{
	qer_editorimage textures/phantgothic/phantgothic_window_002.tga
	q3map_lightimage textures/phantgothic/phantgothic_window_002.tga   
	surfaceparm lightfilter
    q3map_lightmapFilterRadius 0 4
	q3map_surfacelight 100
	{
		map textures/phantgothic/phantgothic_window_002.tga
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
	{
		map textures/sfx/glow_orange_01.tga	
		rgbGen wave sin .35 .35 0 .5	
		blendfunc add
	}
}

textures/se_gothic/rock
{
	q3map_nonplanar
	q3map_shadeangle 60
	{
 		map $lightmap
 		rgbGen identity
 	}
 	{
 		map textures/se_gothic/rock.tga
 		blendfunc filter
 	}
}

textures/se_gothic/rock_etched
{
	q3map_nonplanar
	q3map_shadeangle 60
	{
 		map $lightmap
 		rgbGen identity
 	}
 	{
 		map textures/se_gothic/rock_etched.tga
 		blendfunc filter
 	}
}

textures/se_gothic/rock2
{
	q3map_nonplanar
	q3map_shadeangle 60
	{
 		map $lightmap
 		rgbGen identity
 	}
 	{
 		map textures/se_gothic/rock2.tga
 		blendfunc filter
 	}
}

textures/se_gothic/rock3
{
	q3map_nonplanar
	q3map_shadeangle 60
	{
 		map $lightmap
 		rgbGen identity
 	}
 	{
 		map textures/se_gothic/rock3.tga
 		blendfunc filter
 	}
}

textures/se_gothic/rock3_dirty
{
	q3map_nonplanar
	q3map_shadeangle 60
	{
 		map $lightmap
 		rgbGen identity
 	}
 	{
 		map textures/se_gothic/rock3_dirty.tga
		//tcMod scale 1 1 
 		blendfunc filter
 	}
}

textures/se_gothic/rock3_basetrimmed
{
	qer_editorimage textures/se_gothic/rock3_basetrimmed_ed.tga
	q3map_nonplanar
	q3map_shadeangle 60
	{
 		map $lightmap
 		rgbGen identity
 	}
 	{
 		map textures/se_gothic/rock3_basetrimmed.tga
		//tcMod scale 1 1
 		blendfunc filter
 	}
}

textures/se_gothic/rivets_01
{
	qer_editorimage textures/se_gothic/rivets_01.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/rivets_01.tga
		blendfunc filter
	}
}

textures/se_gothic/rivets_02
{
	qer_editorimage textures/se_gothic/rivets_02.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/rivets_02.tga
		blendfunc filter
	}
}

textures/se_gothic/rivets_02_nonsolid
{
	qer_editorimage textures/se_gothic/rivets_02.tga
	surfaceparm	nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/rivets_02.tga
		blendfunc filter
	}
}

textures/se_gothic/rivets_03
{
	qer_editorimage textures/se_gothic/rivets_03.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/rivets_03.tga
		blendfunc filter
	}
}

textures/se_gothic/rune_black
{
	qer_editorimage textures/se_gothic/rune_black_flat.tga
	q3map_lightimage textures/se_gothic/rune_black.blend.tga
	surfaceparm nomarks
	q3map_surfacelight 400
	novlcollapse
	nopicmip
	{
		map $lightmap 
		rgbGen identity
		tcGen lightmap 
	}
	{
		map textures/se_gothic/rune_black_flat.tga
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/se_gothic/rune_black.blend.tga
		rgbGen wave sin 0.75 0.35 0 .25
		blendfunc add
	}
}

textures/se_gothic/rune_black_flat_nonsolid
{
	qer_editorimage textures/se_gothic/rune_black_flat.tga
	surfaceparm nonsolid
	sort 6
	polygonOffset
	nopicmip
	{
		map $lightmap 
		rgbGen identity
		tcGen lightmap 
	}
	{
		map textures/se_gothic/rune_black_flat.tga
		blendfunc filter
		rgbGen identity
	}
}

textures/se_gothic/rune_earth
{
	qer_editorimage textures/se_gothic/rune_earth_flat.tga
	q3map_lightimage textures/se_gothic/rune_earth.blend.tga
	surfaceparm nomarks
	q3map_surfacelight 400
	novlcollapse
	nopicmip
	{
		map $lightmap 
		rgbGen identity
		tcGen lightmap 
	}
	{
		map textures/se_gothic/rune_earth_flat.tga
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/se_gothic/rune_earth.blend.tga
		rgbGen wave sin 0.75 0.35 0 .25
		blendfunc add
	}
}

textures/se_gothic/rune_elder
{
	qer_editorimage textures/se_gothic/rune_elder_flat.tga
	q3map_lightimage textures/se_gothic/rune_elder.blend.tga
	surfaceparm nomarks
	q3map_surfacelight 400
	novlcollapse
	nopicmip
	{
		map $lightmap 
		rgbGen identity
		tcGen lightmap 
	}
	{
		map textures/se_gothic/rune_elder_flat.tga
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/se_gothic/rune_elder.blend.tga
		rgbGen wave sin 0.75 0.35 0 .25
		blendfunc add
	}
}

textures/se_gothic/rune_elder_flat_nonsolid
{
	qer_editorimage textures/se_gothic/rune_elder_flat.tga
	surfaceparm nonsolid
	sort 6
	polygonOffset
	nopicmip
	{
		map $lightmap 
		rgbGen identity
		tcGen lightmap 
	}
	{
		map textures/se_gothic/rune_elder_flat.tga
		blendfunc filter
		rgbGen identity
	}
}

textures/se_gothic/rune_hell
{
	qer_editorimage textures/se_gothic/rune_hell_flat.tga
	q3map_lightimage textures/se_gothic/rune_hell.blend.tga
	surfaceparm nomarks
	q3map_surfacelight 400
	novlcollapse
	nopicmip
	{
		map $lightmap 
		rgbGen identity
		tcGen lightmap 
	}
	{
		map textures/se_gothic/rune_hell_flat.tga
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/se_gothic/rune_hell.blend.tga
		rgbGen wave sin 0.75 0.35 0 .25
		blendfunc add
	}
}

textures/se_gothic/runesheet
{
	qer_editorimage textures/se_gothic/runesheet.tga
	q3map_surfacelight 400
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	polygonOffset
	sort 6
	{
		map textures/se_gothic/runesheet.tga
		rgbGen wave sin 0.25 .65 0 0.1
		blendfunc add
	}
}

textures/se_gothic/se_godray
{
	surfaceparm nolightmap
	surfaceparm trans
	cull disable
	deformVertexes autosprite2
	qer_trans 0.70
	nopicmip
	{
		map textures/se_gothic/se_godray.tga
		blendfunc add
		rgbGen identity
	}
}

textures/se_gothic/se_skyflare
{
	surfaceparm nolightmap
	surfaceparm trans
	cull disable
	deformVertexes autosprite
	qer_trans 0.70
	nopicmip
	{
		map textures/se_gothic/se_skyflare.tga
		blendfunc add
		rgbGen identity
	}
}

textures/se_gothic/stainglass_01
{
	surfaceparm trans		
	surfaceparm nolightmap
	cull none
      nopicmip
	qer_trans 0.6

	{
		map textures/se_gothic/stainglass_01.tga
		blendfunc filter
		rgbGen identity
	}
}

textures/se_gothic/stainglass_02
{
	surfaceparm trans		
	surfaceparm nolightmap
	cull none
      nopicmip
	qer_trans 0.6

	{
		map textures/se_gothic/stainglass_02.tga
		blendfunc filter
		rgbGen identity
	}
}

textures/se_gothic/stainglass_03
{
	surfaceparm trans		
	surfaceparm nolightmap
	cull none
      nopicmip
	qer_trans 0.6

	{
		map textures/se_gothic/stainglass_03.tga
		blendfunc filter
		rgbGen identity
	}
}

textures/se_gothic/stainglass_04
{
	surfaceparm trans		
	surfaceparm nolightmap
	cull none
      nopicmip
	qer_trans 0.4

	{
		map textures/se_gothic/stainglass_04.tga
		blendfunc filter
		rgbGen identity
	}
}

textures/se_gothic/steprister_8
{
	qer_editorimage textures/se_gothic/stepriser_8.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/stepriser_8.tga
		blendfunc filter
	}
}

textures/se_gothic/steprister2_8
{
	qer_editorimage textures/se_gothic/stepriser2_8.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/stepriser2_8.tga
		blendfunc filter
	}
}

textures/se_gothic/steptread_16
{
	qer_editorimage textures/se_gothic/steptread_16.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/steptread_16.tga
		blendfunc filter
	}
}

textures/se_gothic/steptread2_16
{
	qer_editorimage textures/se_gothic/steptread2_16.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/steptread2_16.tga
		blendfunc filter
	}
}

textures/se_gothic/steptread3_16
{
	qer_editorimage textures/se_gothic/steptread3_16.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/steptread3_16.tga
		blendfunc filter
	}
}

textures/se_gothic/steptread_32
{
	qer_editorimage textures/se_gothic/steptread_32.tga
	surfaceparm	metalsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/steptread_32.tga
		blendfunc filter
	}
}

textures/terrain/stonekeep_dirt1_pond1
{
      qer_editorimage textures/terrain/qzterra1_dirt1_pond1_ed.tga
	surfaceparm dust
	q3map_nonplanar
	q3map_shadeangle 120
	q3map_tcGen ivector ( 256 0 0 ) ( 0 256 0 )
	q3map_alphaMod dotproduct2 ( 0 0 1 )
	q3map_globaltexture
	novlcollapse
	{
		map textures/terrain/stonekeep_dirt1.tga	// Primary (dp2 Vertical)
		rgbGen identity
	}
	{
		map textures/terrain/qzterra1_pond1.tga	// Secondary (dp2 Horizontal)
		blendfunc blend
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/terrain/stonekeep_dirt1_grass1
{
      qer_editorimage textures/terrain/qzterra1_dirt1_grass1_ed.tga
	surfaceparm dust
	q3map_nonplanar
	q3map_shadeangle 120
	q3map_tcGen ivector ( 256 0 0 ) ( 0 256 0 )
	q3map_alphaMod dotproduct2 ( 0 0 1 )
	q3map_globaltexture
	novlcollapse
	{
		map textures/terrain/stonekeep_dirt1.tga	// Primary (dp2 Vertical)
		tcmod scale 2 2
		rgbGen identity
	}
	{
		map textures/terrain/qzterra1_grass1.tga	// Secondary (dp2 Horizontal)
		tcmod scale 2 2
		blendfunc blend
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/terrain/stonekeep_dirt1_ground
{
      qer_editorimage textures/terrain/qzterra1_dirt1_grass1_ed.tga
	surfaceparm dust
	q3map_nonplanar
	q3map_shadeangle 120
	q3map_tcGen ivector ( 256 0 0 ) ( 0 256 0 )
	q3map_alphaMod dotproduct2 ( 0 0 1 )
	q3map_globaltexture
	novlcollapse
	{
		map textures/se_gothic/ground.tga	// Primary (dp2 Vertical)
		tcmod scale 2 2
		rgbGen identity
	}
	{
		map textures/terrain/qzterra1_grass1.tga	// Secondary (dp2 Horizontal)
		tcmod scale 2 2
		blendfunc blend
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/terrain/stonekeep_rock1_grass1
{
      qer_editorimage textures/terrain/qzterra1_rock1_grass1_ed.tga
	surfaceparm dust
	q3map_nonplanar
	q3map_shadeangle 120
	q3map_tcGen ivector ( 256 0 0 ) ( 0 256 0 )
	q3map_alphaMod dotproduct2 ( 0 0 1 )
	q3map_globaltexture
	novlcollapse
	{
		map textures/terrain/stonekeep_rock1.tga	// Primary (dp2 Vertical)
		rgbGen identity
	}
	{
		map textures/terrain/qzterra1_grass1.tga	// Secondary (dp2 Horizontal)
		tcmod scale 2 2
		blendfunc blend
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/terrain/stonekeep_rock1_rock2
{
    qer_editorimage textures/terrain/qzterra1_rock1_rock2_ed.tga
	q3map_nonplanar
	q3map_shadeangle 120
	q3map_tcGen ivector ( 256 0 0 ) ( 0 256 0 )
	q3map_alphaMod dotproduct2 ( 0 0 1 )
	q3map_globaltexture
	novlcollapse
	{
		map textures/terrain/stonekeep_rock1.tga	// Primary (dp2 Vertical)
		rgbGen identity
	}
	{
		map textures/terrain/stonekeep_rock2.tga	// Secondary (dp2 Horizontal)
		blendfunc blend
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/se_gothic/stonekeep_moss_rock
{
    qer_editorimage textures/se_gothic/moss.tga
	novlcollapse
	{
		map textures/se_gothic/moss.tga	// Primary (dp2 Vertical)
		rgbGen identity
	}
	{
		map textures/se_gothic/rock.tga	// Secondary (dp2 Horizontal)
		tcmod scale 2 2
		blendfunc blend
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/se_gothic/stonekeep_moss2_rock
{
      qer_editorimage textures/se_gothic/moss2.tga
	novlcollapse
	{
		map textures/se_gothic/moss2.tga	// Primary (dp2 Vertical)
		rgbGen identity
	}
	{
		map textures/se_gothic/rock.tga	// Secondary (dp2 Horizontal)
		tcmod scale 2 2
		blendfunc blend
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/se_gothic/stonekeep_moss3_rock
{
      qer_editorimage textures/se_gothic/moss3.tga
	novlcollapse
	{
		map textures/se_gothic/moss3.tga	// Primary (dp2 Vertical)
		rgbGen identity
	}
	{
		map textures/se_gothic/rock.tga	// Secondary (dp2 Horizontal)
		tcmod scale 2 2
		blendfunc blend
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/se_gothic/stoneslab_01
{
	qer_editorimage textures/se_gothic/stoneslab_01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/stoneslab_01.tga
		blendfunc filter
	}
}

textures/se_gothic/tele_dest_01
{
	qer_editorimage textures/se_gothic/tele_dest_01.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	polygonOffset
	sort 6
	{
		map textures/se_gothic/tele_dest_01.tga
		blendfunc add
	}
	{
		map textures/se_gothic/tele_dest_02.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/tele_dest_02
{
	qer_editorimage textures/se_gothic/tele_dest_02.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/se_gothic/tele_dest_02.add.tga
		blendfunc add
	}
	{
		map textures/se_gothic/tele_dest_02.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/tele_dest_02.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/se_gothic/tile_01
{
	qer_editorimage textures/se_gothic/tile_01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/tile_01.tga
		tcmod scale 2 2
		blendfunc filter
	}
}

textures/se_gothic/tile_02
{
	qer_editorimage textures/se_gothic/tile_02.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/tile_02.tga
		blendfunc filter
	}
}

textures/se_gothic/tile_03
{
	qer_editorimage textures/se_gothic/tile_03.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/tile_03.tga
		blendfunc filter
	}
}

textures/se_gothic/tile_04
{
	qer_editorimage textures/se_gothic/tile_04.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/tile_04.tga
		blendfunc filter
	}
}

textures/se_gothic/tile_04_floordesign
{
	qer_editorimage textures/se_gothic/tile_04_floordesign.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/tile_04_floordesign.tga
		blendfunc filter
	}
}

textures/se_gothic/tile_05
{
	qer_editorimage textures/se_gothic/tile_05.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/tile_05.tga
		blendfunc filter
	}
}

textures/se_gothic/tile_06
{
	qer_editorimage textures/se_gothic/tile_06.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/tile_06.tga
		blendfunc filter
	}
}

textures/se_gothic/tile_07
{
	qer_editorimage textures/se_gothic/tile_07.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/tile_07.tga
		blendfunc filter
	}
}

textures/se_gothic/vine_growth
{
   	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm alphashadow
	nopicmip
	qer_trans .75
	cull none	
	qer_editorimage textures/se_industrial/vine_growth.tga
	{
		map textures/se_industrial/vine_growth.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
}


textures/se_gothic/wagon_wheel
{
	surfaceparm trans		
	surfaceparm nonsolid
	surfaceparm	metalsteps
	surfaceparm alphashadow
	surfaceparm nomarks
	cull none
    nopicmip
	{
		map textures/se_gothic/wagon_wheel.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap 
		blendfunc filter
		rgbGen identity
		tcGen lightmap 
		depthFunc equal
	}
}

textures/se_gothic/wood_01
{
	qer_editorimage textures/se_gothic/wood_01.tga
	surfaceparm	woodsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/wood_01.tga
		blendfunc filter
	}
}

textures/se_gothic/wood_02
{
	qer_editorimage textures/se_gothic/wood_02.tga
	surfaceparm	woodsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/wood_02.tga
		blendfunc filter
	}
}

textures/se_gothic/wood_03
{
	qer_editorimage textures/se_gothic/wood_03.tga
	surfaceparm	woodsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/wood_03.tga
		blendfunc filter
	}
}

textures/se_gothic/wood_04
{
	qer_editorimage textures/se_gothic/wood_04.tga
	surfaceparm	woodsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/wood_04.tga
		blendfunc filter
	}
}

textures/se_gothic/wood_05
{
	qer_editorimage textures/se_gothic/wood_05.tga
	surfaceparm	woodsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/wood_05.tga
		blendfunc filter
	}
}

textures/se_gothic/wood_06
{
	qer_editorimage textures/se_gothic/wood_06.tga
	surfaceparm	woodsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/wood_06.tga
		blendfunc filter
	}
}

textures/se_gothic/wood_07
{
	qer_editorimage textures/se_gothic/wood_07.tga
	surfaceparm	woodsteps
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/wood_07.tga
		blendfunc filter
	}
}